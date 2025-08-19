#!/usr/bin/env python3
"""
GUI interface for RabbitMQ monitoring using tkinter
"""
import time
import asyncio
import logging
import threading
from typing import Dict
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json

from .monitor import ExchangeMonitor

logger = logging.getLogger(__name__)


class RoutingKeyViewerWindow:
    """Window for viewing messages from a specific routing key."""
    
    def __init__(self, parent, exchange_name: str, routing_key: str,
                 monitor: ExchangeMonitor):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.monitor = monitor
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Messages - {exchange_name} → {routing_key}")
        self.window.geometry("900x700")
        
        self._setup_ui()
        self._load_messages()
        self._start_auto_refresh()
        
    def _setup_ui(self):
        """Setup the routing key message viewer UI."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text=f"Exchange: {self.exchange_name}",
            font=("Arial", 12, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(
            header_frame,
            text=f"Routing Key: {self.routing_key}",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            header_frame,
            text="Auto Refresh",
            variable=self.auto_refresh_var
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            header_frame,
            text="Refresh",
            command=self._load_messages
        ).pack(side=tk.RIGHT)
        
        # Message list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.message_listbox = tk.Listbox(list_scroll_frame)
        self.message_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.message_listbox.bind('<<ListboxSelect>>', self._on_message_select)
        
        list_scrollbar = ttk.Scrollbar(
            list_scroll_frame,
            orient=tk.VERTICAL,
            command=self.message_listbox.yview
        )
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # Message details
        details_frame = ttk.LabelFrame(list_frame, text="Message Details")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.message_details = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            width=40
        )
        self.message_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _load_messages(self):
        """Load messages for the routing key."""
        try:
            messages = self.monitor.get_routing_key_messages(
                self.exchange_name, self.routing_key
            )
            
            # Debug: Check what we actually have in the monitor
            all_exchange_messages = self.monitor.exchange_messages.get(
                self.exchange_name, []
            )
            routing_key_stats = self.monitor.routing_key_messages.get(
                self.exchange_name, {}
            )
            
            logger.info(
                f"🔍 Debug - Total messages in exchange '{self.exchange_name}': "
                f"{len(all_exchange_messages)}"
            )
            logger.info(
                f"🔍 Debug - Routing keys in exchange: {list(routing_key_stats.keys())}"
            )
            logger.info(
                f"🔍 Debug - Messages for routing key '{self.routing_key}': "
                f"{len(messages)}"
            )
            
            # Clear current list
            self.message_listbox.delete(0, tk.END)
            self.messages = messages
            
            # Add messages to list
            for i, message in enumerate(messages):
                timestamp = message.get('timestamp', 'Unknown')
                display_text = f"{i+1:3d}. {timestamp}"
                self.message_listbox.insert(tk.END, display_text)
                
            logger.info(
                f"📊 Loaded {len(messages)} messages for "
                f"{self.exchange_name} → {self.routing_key}"
            )
            
            # Update window title with message count
            self.window.title(
                f"Messages ({len(messages)}) - {self.exchange_name} → {self.routing_key}"
            )
            
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            messagebox.showerror("Error", f"Failed to load messages: {e}")
            
    def _on_message_select(self, event):
        """Handle message selection."""
        selection = self.message_listbox.curselection()
        if not selection:
            return
            
        try:
            message_index = selection[0]
            message = self.messages[message_index]
            
            # Format message details
            details = {
                'Timestamp': message.get('timestamp', 'Unknown'),
                'Exchange': message.get('exchange', 'Unknown'),
                'Routing Key': message.get('routing_key', 'Unknown'),
                'Trace Type': message.get('trace_type', 'Unknown'),
                'Properties': message.get('properties', {}),
                'Body': message.get('body', {}),
                'Raw Body': message.get('raw_body', '')
            }
            
            # Display formatted JSON
            formatted_details = json.dumps(details, indent=2, default=str)
            
            self.message_details.delete(1.0, tk.END)
            self.message_details.insert(1.0, formatted_details)
            
        except Exception as e:
            logger.error(f"Error displaying message details: {e}")
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer."""
        self._schedule_auto_refresh()
    
    def _schedule_auto_refresh(self):
        """Schedule the next auto-refresh."""
        if self.auto_refresh_var.get():
            self._load_messages()
        # Schedule next refresh in 2 seconds
        self.window.after(2000, self._schedule_auto_refresh)


class MessageViewerWindow:
    """Window for viewing messages from a specific exchange with routing key organization."""
    
    def __init__(self, parent, exchange_name: str, monitor: ExchangeMonitor):
        self.exchange_name = exchange_name
        self.monitor = monitor
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Exchange Messages - {exchange_name}")
        self.window.geometry("1000x700")
        
        self._setup_ui()
        self._load_routing_keys()
        self._start_auto_refresh()
        
    def _setup_ui(self):
        """Setup the exchange message viewer UI with routing key hierarchy."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text=f"Exchange: {self.exchange_name}",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            header_frame,
            text="Auto Refresh",
            variable=self.auto_refresh_var
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            header_frame,
            text="Refresh",
            command=self._load_routing_keys
        ).pack(side=tk.RIGHT)
        
        # Split view: Routing keys on left, summary on right
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Routing keys
        left_frame = ttk.LabelFrame(paned_window, text="Routing Keys")
        paned_window.add(left_frame, weight=1)
        
        self.routing_key_listbox = tk.Listbox(left_frame)
        self.routing_key_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.routing_key_listbox.bind(
            '<Double-1>', self._on_routing_key_double_click
        )
        
        # Right panel: Summary and recent messages
        right_frame = ttk.LabelFrame(paned_window, text="Summary")
        paned_window.add(right_frame, weight=2)
        
        # Stats frame
        stats_frame = ttk.Frame(right_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(
            stats_frame, text="Select a routing key to view details"
        )
        self.stats_label.pack()
        
        # Recent messages preview
        preview_frame = ttk.LabelFrame(right_frame, text="Recent Messages Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, wrap=tk.WORD, height=15
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _load_routing_keys(self):
        """Load routing keys for the exchange."""
        try:
            routing_keys = self.monitor.get_exchange_routing_keys(self.exchange_name)
            total_messages = self.monitor.get_all_stats().get(self.exchange_name, 0)
            
            # Debug: Check what we actually have in the monitor
            all_exchange_messages = self.monitor.exchange_messages.get(
                self.exchange_name, []
            )
            routing_key_data = self.monitor.routing_key_messages.get(
                self.exchange_name, {}
            )
            
            logger.info(
                f"🔍 Debug Exchange '{self.exchange_name}' - Stats total: {total_messages}"
            )
            logger.info(
                f"🔍 Debug Exchange '{self.exchange_name}' - "
                f"Direct messages: {len(all_exchange_messages)}"
            )
            logger.info(
                f"🔍 Debug Exchange '{self.exchange_name}' - "
                f"Routing keys found: {routing_keys}"
            )
            logger.info(
                f"🔍 Debug Exchange '{self.exchange_name}' - "
                f"Routing key data: {list(routing_key_data.keys())}"
            )
            
            # Clear current list
            self.routing_key_listbox.delete(0, tk.END)
            
            # Add routing keys with message counts
            routing_key_stats = {}
            for rk in routing_keys:
                messages = self.monitor.get_routing_key_messages(self.exchange_name, rk)
                routing_key_stats[rk] = len(messages)
                logger.info(f"🔍 Debug - Routing key '{rk}': {len(messages)} messages")
            
            # Sort by message count (descending)
            sorted_keys = sorted(routing_key_stats.items(), key=lambda x: -x[1])
            
            for routing_key, count in sorted_keys:
                display_text = f"{routing_key} ({count} messages)"
                self.routing_key_listbox.insert(tk.END, display_text)
            
            # Update stats
            self.stats_label.config(text=f"Total: {len(routing_keys)} routing keys, {total_messages} messages")
            
            # Update window title with message count
            self.window.title(f"Exchange Messages ({total_messages}) - {self.exchange_name}")
            
            # Load preview
            self._load_preview()
            
            logger.info(
                f"📊 Loaded {len(routing_keys)} routing keys for exchange "
                f"{self.exchange_name}"
            )
            
        except Exception as e:
            logger.error(f"Error loading routing keys: {e}")
            messagebox.showerror("Error", f"Failed to load routing keys: {e}")
            
    def _load_preview(self):
        """Load a preview of recent messages."""
        try:
            messages = self.monitor.get_exchange_messages(
                self.exchange_name, limit=50
            )
            
            preview_text = f"Recent Messages for Exchange '{self.exchange_name}':\n"
            preview_text += "=" * 60 + "\n\n"
            
            # Show last 10 messages
            for i, message in enumerate(messages[-10:], 1):
                timestamp = message.get('timestamp', 'Unknown')
                routing_key = message.get('routing_key', 'Unknown')
                trace_type = message.get('trace_type', 'Unknown')
                
                preview_text += f"{i}. {timestamp}\n"
                preview_text += f"   Routing Key: {routing_key}\n"
                preview_text += f"   Type: {trace_type}\n"
                preview_text += "-" * 40 + "\n"
            
            if not messages:
                preview_text += "No messages found yet.\n\n"
                preview_text += (
                    "Make sure RabbitMQ tracing is enabled and messages are being "
                    "published to this exchange."
                )
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
            
        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            
    def _on_routing_key_double_click(self, event):
        """Handle double-click on routing key to open detailed view."""
        selection = self.routing_key_listbox.curselection()
        if not selection:
            return
            
        try:
            selected_text = self.routing_key_listbox.get(selection[0])
            # Extract routing key from "routing_key (X messages)" format
            routing_key = selected_text.split(' (')[0]
            
            # Open routing key viewer window
            RoutingKeyViewerWindow(
                self.window, self.exchange_name, routing_key, self.monitor
            )
            
        except Exception as e:
            logger.error(f"Error opening routing key viewer: {e}")
            messagebox.showerror("Error", f"Failed to open routing key viewer: {e}")
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer."""
        self._schedule_auto_refresh()
    
    def _schedule_auto_refresh(self):
        """Schedule the next auto-refresh."""
        if self.auto_refresh_var.get():
            self._load_routing_keys()
            self._load_preview()
        # Schedule next refresh in 2 seconds
        self.window.after(2000, self._schedule_auto_refresh)


class GUIInterface:
    """GUI interface for RabbitMQ monitoring."""
    
    def __init__(self, monitor: ExchangeMonitor):
        self.monitor = monitor
        self.root = tk.Tk()
        self.running = False
        self.loop = None
        self.loop_thread = None
        
        self._setup_ui()
        self._setup_monitor_callbacks()
        self._start_async_loop()
        
    def _setup_ui(self):
        """Setup the main GUI."""
        self.root.title("RabbitMQ Exchange Monitor")
        self.root.geometry("900x700")
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="🐰 RabbitMQ Exchange Monitor",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # Connection status
        self.status_label = ttk.Label(
            header_frame, text="Disconnected", foreground="red"
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Connection configuration frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings")
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # First row: Host and Port
        conn_row1 = ttk.Frame(conn_frame)
        conn_row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conn_row1, text="Host:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar(value=self.monitor.host)
        self.host_entry = ttk.Entry(
            conn_row1, textvariable=self.host_var, width=20
        )
        self.host_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(conn_row1, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value=str(self.monitor.port))
        self.port_entry = ttk.Entry(
            conn_row1, textvariable=self.port_var, width=8
        )
        self.port_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Second row: Username and Password
        conn_row2 = ttk.Frame(conn_frame)
        conn_row2.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(conn_row2, text="Username:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar(value=self.monitor.username)
        self.username_entry = ttk.Entry(
            conn_row2, textvariable=self.username_var, width=15
        )
        self.username_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(conn_row2, text="Password:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar(value=self.monitor.password)
        self.password_entry = ttk.Entry(
            conn_row2,
            textvariable=self.password_var,
            width=15,
            show="*"
        )
        self.password_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Third row: Trace Queue
        conn_row3 = ttk.Frame(conn_frame)
        conn_row3.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(conn_row3, text="Trace Queue:").pack(side=tk.LEFT)
        self.trace_queue_var = tk.StringVar(value="trace")
        self.trace_queue_entry = ttk.Entry(
            conn_row3, textvariable=self.trace_queue_var, width=20
        )
        self.trace_queue_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.connect_button = ttk.Button(
            button_frame, text="Connect", command=self._toggle_connection
        )
        self.connect_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, text="Reset Stats", command=self._reset_stats
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, text="Refresh", command=self._refresh_display
        ).pack(side=tk.LEFT)
        
        # Exchange list
        list_frame = ttk.LabelFrame(main_frame, text="Exchanges")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for exchanges
        columns = ("Exchange", "Message Count", "Last Update")
        self.exchange_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings"
        )
        
        # Configure columns
        self.exchange_tree.heading("Exchange", text="Exchange Name")
        self.exchange_tree.heading("Message Count", text="Message Count")
        self.exchange_tree.heading("Last Update", text="Last Update")
        
        self.exchange_tree.column("Exchange", width=300)
        self.exchange_tree.column("Message Count", width=150)
        self.exchange_tree.column("Last Update", width=200)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.exchange_tree.yview
        )
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exchange_tree.config(yscrollcommand=tree_scrollbar.set)
        
        self.exchange_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.exchange_tree.bind(
            '<Double-1>', self._on_exchange_double_click
        )
        
        # Status bar
        self.status_bar = ttk.Label(
            main_frame, text="Ready", relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_monitor_callbacks(self):
        """Setup callbacks for monitor updates."""
        self.monitor.add_update_callback(self._on_exchange_update)
    
    def _start_async_loop(self):
        """Start the background asyncio event loop in a separate thread."""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        
        # Wait a moment for the loop to start
        time.sleep(0.1)
    
    def _stop_async_loop(self):
        """Stop the background asyncio event loop."""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.loop_thread:
            self.loop_thread.join(timeout=1.0)
        
    def _toggle_connection(self):
        """Toggle connection to RabbitMQ."""
        if not self.running:
            self._connect()
        else:
            self._disconnect()
            
    def _connect(self):
        """Connect to RabbitMQ and start monitoring."""
        try:
            # Schedule the async connect on the background event loop
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(self._async_connect(), self.loop)
                # Don't wait for result here - let it run asynchronously
            else:
                logger.error("Background event loop not available")
                messagebox.showerror("Error", "Background event loop not available")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self._set_connection_fields_state('normal')
            
    async def _async_connect(self):
        """Async implementation of connect logic."""
        try:
            # Update monitor settings from GUI fields
            self.monitor.host = self.host_var.get().strip()
            self.monitor.port = int(self.port_var.get().strip())
            self.monitor.username = self.username_var.get().strip()
            self.monitor.password = self.password_var.get().strip()
            self.monitor.trace_queue_name = (
                self.trace_queue_var.get().strip() or "trace"
            )
            
            logger.info(
                f"Connecting to RabbitMQ at {self.monitor.host}:{self.monitor.port}"
            )
            
            # Disable connection fields during connection attempt
            self._set_connection_fields_state('disabled')
            
            # Try to connect
            success, error_msg = await self.monitor.connect()
            if success:
                # Try to start monitoring
                monitor_success, monitor_error = await self.monitor.start_monitoring()
                if monitor_success:
                    self.running = True
                    # Update GUI elements on main thread
                    self.root.after(0, self._on_connection_success)
                    logger.info("✅ Connected and monitoring started")
                else:
                    logger.error(f"Failed to start monitoring: {monitor_error}")
                    await self.monitor.disconnect()
                    # Update GUI on main thread
                    error_msg = f"Failed to start monitoring:\n\n{monitor_error}"
                    self.root.after(0, lambda: self._on_connection_error(error_msg))
            else:
                logger.error(f"Failed to connect to RabbitMQ: {error_msg}")
                # Update GUI on main thread
                connection_error_msg = f"Failed to connect to RabbitMQ:\n\n{error_msg}"
                self.root.after(
                    0, lambda: self._on_connection_error(connection_error_msg)
                )
                
        except ValueError as port_error:
            logger.error(f"Invalid port number: {port_error}")
            messagebox.showerror("Error", "Please enter a valid port number")
            self._set_connection_fields_state('normal')
        except Exception as connection_error:
            logger.error(f"Connection error: {connection_error}")
            error_msg = f"Connection failed: {connection_error}"
            self.root.after(0, lambda: self._on_connection_error(error_msg))
    
    def _on_connection_success(self):
        """Handle successful connection on the main GUI thread."""
        self.connect_button.config(text="Disconnect")
        self.status_label.config(text="Connected", foreground="green")
        self.status_bar.config(text="Monitoring started")
        
        # Start update loop
        self._start_update_loop()
    
    def _on_connection_error(self, error_message: str):
        """Handle connection error on the main GUI thread."""
        messagebox.showerror("Connection Error", error_message)
        self._set_connection_fields_state('normal')
            
    def _disconnect(self):
        """Disconnect from RabbitMQ."""
        try:
            # Schedule the async disconnect on the background event loop
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_disconnect(), self.loop
                )
                # Wait for disconnect to complete (should be quick)
                future.result(timeout=5.0)
            else:
                logger.warning("Background event loop not available for disconnect")
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
            
    async def _async_disconnect(self):
        """Async implementation of disconnect logic."""
        try:
            self.running = False
            await self.monitor.stop_monitoring()
            await self.monitor.disconnect()
            
            # Update GUI on main thread
            self.root.after(0, self._on_disconnection_success)
            
            logger.info("👋 Disconnected from RabbitMQ")
            
        except Exception as e:
            logger.error(f"Disconnection error: {e}")
    
    def _on_disconnection_success(self):
        """Handle successful disconnection on the main GUI thread."""
        self.connect_button.config(text="Connect")
        self.status_label.config(text="Disconnected", foreground="red")
        self.status_bar.config(text="Disconnected")
        
        # Re-enable connection fields
        self._set_connection_fields_state('normal')
            
    def _set_connection_fields_state(self, state):
        """Enable or disable connection input fields."""
        self.host_entry.config(state=state)
        self.port_entry.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        self.trace_queue_entry.config(state=state)
        
    def _start_update_loop(self):
        """Start the GUI update loop using tkinter's after method."""
        self._schedule_update()
        
    def _schedule_update(self):
        """Schedule the next GUI update."""
        if self.running:
            self._refresh_display()
            # Schedule next update in 500ms (0.5 seconds) for more responsive updates
            self.root.after(500, self._schedule_update)
        
    def _refresh_display(self):
        """Refresh the exchange display."""
        try:
            stats = self.monitor.get_all_stats()
            
            # Clear current items
            for item in self.exchange_tree.get_children():
                self.exchange_tree.delete(item)
                
            # Sort exchanges by message count (descending) then by name
            sorted_exchanges = sorted(
                stats.items(), key=lambda x: (-x[1], x[0])
            )
            
            # Add current exchanges to the tree
            for exchange_name, message_count in sorted_exchanges:
                last_update = time.strftime('%H:%M:%S')
                self.exchange_tree.insert(
                    '', tk.END,
                    values=(exchange_name, f"{message_count:,}", last_update)
                )
                
            # Update status bar
            total_messages = sum(stats.values())
            status_text = (
                f"Last update: {time.strftime('%H:%M:%S')} - {len(stats)} exchanges - "
                f"{total_messages:,} total messages"
            )
            self.status_bar.config(text=status_text)
            
        except Exception as e:
            logger.error(f"Error refreshing display: {e}")
            
    def _reset_stats(self):
        """Reset monitoring statistics."""
        if messagebox.askyesno(
            "Reset Stats", "Are you sure you want to reset all statistics?"
        ):
            self.monitor.reset_stats()
            self._refresh_display()
            logger.info("Statistics reset")
            
    def _on_exchange_update(self, exchange_name: str, message_count: int):
        """Handle exchange update callback."""
        # This runs in the monitor thread, so we need to schedule GUI update on main thread
        self.root.after(
            0, lambda: self._handle_exchange_update(exchange_name, message_count)
        )
        
    def _handle_exchange_update(self, exchange_name: str, message_count: int):
        """Handle exchange update on the main GUI thread."""
        logger.info(
            f"📊 GUI Update: Exchange '{exchange_name}' now has "
            f"{message_count} messages"
        )
        
        # Force a refresh of the main display to show new data
        if self.running:
            self._refresh_display()
            
        # Also refresh any open MessageViewerWindows
        # Note: In a production app, you'd track open windows and update them
        
    def _on_exchange_double_click(self, event):
        """Handle double-click on exchange to view messages."""
        selection = self.exchange_tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            exchange_name = self.exchange_tree.item(item, "values")[0]
            MessageViewerWindow(self.root, exchange_name, self.monitor)
        except Exception as e:
            logger.error(f"Error opening message viewer: {e}")
            messagebox.showerror("Error", f"Failed to open message viewer: {e}")
            
    def _on_closing(self):
        """Handle application closing."""
        if self.running:
            self._disconnect()
        self._stop_async_loop()
        self.root.destroy()
        
    def start(self):
        """Start the GUI application with async support."""
        logger.info("🐰 RabbitMQ Exchange Monitor - GUI Mode")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        finally:
            # Clean up any pending async operations
            if self.running:
                self._disconnect()
            self._stop_async_loop()

