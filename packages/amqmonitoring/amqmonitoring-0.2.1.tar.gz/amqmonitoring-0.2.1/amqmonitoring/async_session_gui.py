#!/usr/bin/env python3
"""
Async-compatible session management GUI components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AsyncSessionListWindow:
    """Async-compatible window for managing monitoring sessions."""
    
    def __init__(self, parent, monitor, event_loop):
        self.parent = parent
        self.monitor = monitor
        self.loop = event_loop
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("Session Manager")
        self.window.geometry("1000x600")
        
        self._setup_ui()
        self._load_sessions()
        
    def _setup_ui(self):
        """Setup the session management UI."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="📁 Session Manager",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(
            header_frame,
            text="Refresh",
            command=self._load_sessions
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            header_frame,
            text="Delete Session",
            command=self._delete_session
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Split view: Sessions list on left, details on right
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Sessions list
        left_frame = ttk.LabelFrame(paned_window, text="Sessions")
        paned_window.add(left_frame, weight=1)
        
        # Session treeview
        columns = ("Name", "Start Time", "Duration", "Messages", "Exchanges")
        self.session_tree = ttk.Treeview(
            left_frame, columns=columns, show="headings", height=15
        )
        
        # Configure columns
        self.session_tree.heading("Name", text="Session Name")
        self.session_tree.heading("Start Time", text="Start Time")
        self.session_tree.heading("Duration", text="Duration")
        self.session_tree.heading("Messages", text="Messages")
        self.session_tree.heading("Exchanges", text="Exchanges")
        
        self.session_tree.column("Name", width=200)
        self.session_tree.column("Start Time", width=150)
        self.session_tree.column("Duration", width=100)
        self.session_tree.column("Messages", width=80)
        self.session_tree.column("Exchanges", width=80)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=self.session_tree.yview
        )
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_tree.config(yscrollcommand=tree_scrollbar.set)
        
        self.session_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.session_tree.bind('<Double-1>', self._on_session_double_click)
        self.session_tree.bind('<<TreeviewSelect>>', self._on_session_select)
        
        # Right panel: Session details and actions
        right_frame = ttk.LabelFrame(paned_window, text="Session Details")
        paned_window.add(right_frame, weight=2)
        
        # Session info
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.session_info = tk.Text(info_frame, height=8, wrap=tk.WORD)
        self.session_info.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            action_frame,
            text="View Session Data",
            command=self._view_session_data
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Export Session",
            command=self._export_session
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Exchange list for selected session
        exchange_frame = ttk.LabelFrame(right_frame, text="Exchanges in Session")
        exchange_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.exchange_listbox = tk.Listbox(exchange_frame)
        self.exchange_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.exchange_listbox.bind('<Double-1>', self._on_exchange_double_click)
        
    def _load_sessions(self):
        """Load sessions from database using async event loop."""
        try:
            # Clear current items
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
                
            # Add loading indicator
            self.session_tree.insert(
                '', tk.END,
                values=("Loading sessions...", "...", "...", "...", "...")
            )
            
            # Schedule async loading
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_load_sessions(), self.loop
                )
                # Don't wait for result here - let it update the UI when ready
            else:
                logger.error("No event loop available for async session loading")
                messagebox.showerror("Error", "Event loop not available")
                
        except Exception as e:
            logger.error(f"Error starting session load: {e}")
            messagebox.showerror("Error", f"Failed to start loading sessions: {e}")
    
    async def _async_load_sessions(self):
        """Async method to load sessions and update UI."""
        try:
            sessions = await self.monitor.get_sessions(limit=100)
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_sessions_ui(sessions))
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to load sessions: {e}"))
    
    def _update_sessions_ui(self, sessions: List[Dict]):
        """Update the sessions UI with loaded data."""
        try:
            # Clear loading indicator
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
                
            self.sessions = {}
            
            for session in sessions:
                session_id = session['id']
                name = session['name']
                start_time = session['start_time']
                end_time = session['end_time']
                total_messages = session['total_messages']
                exchanges_count = session['exchanges_count']
                
                # Calculate duration
                if end_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        duration = str(end_dt - start_dt).split('.')[0]  # Remove microseconds
                    except Exception:
                        duration = "Unknown"
                else:
                    duration = "Active"
                
                # Format start time
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_start = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    formatted_start = start_time
                
                # Store session data
                self.sessions[session_id] = session
                
                # Add to tree
                self.session_tree.insert(
                    '', tk.END,
                    values=(name, formatted_start, duration, 
                           f"{total_messages:,}", exchanges_count),
                    tags=(session_id,)
                )
                
            logger.info(f"Loaded {len(sessions)} sessions")
            
        except Exception as e:
            logger.error(f"Error updating sessions UI: {e}")
    
    def _on_session_select(self, event):
        """Handle session selection."""
        selection = self.session_tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            tags = self.session_tree.item(item, "tags")
            if not tags or tags[0] == "loading":
                return
                
            session_id = tags[0]
            session = self.sessions.get(session_id)
            
            if session:
                # Update session info display
                info_text = f"""Session Details:

Name: {session['name']}
Session ID: {session['id']}
Host: {session.get('host', 'Unknown')}
Port: {session.get('port', 'Unknown')}
Username: {session.get('username', 'Unknown')}
Trace Queue: {session.get('trace_queue', 'Unknown')}

Start Time: {session['start_time']}
End Time: {session['end_time'] or 'Still Active'}
Total Messages: {session['total_messages']:,}
Exchanges: {session['exchanges_count']}
"""
                
                self.session_info.delete(1.0, tk.END)
                self.session_info.insert(1.0, info_text)
                
                # Load exchanges for this session
                self._load_session_exchanges(session_id)
                
        except Exception as e:
            logger.error(f"Error selecting session: {e}")
    
    def _load_session_exchanges(self, session_id: str):
        """Load exchanges for selected session."""
        try:
            self.exchange_listbox.delete(0, tk.END)
            self.exchange_listbox.insert(tk.END, "Loading exchanges...")
            
            # Schedule async loading of exchange data
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_load_session_exchanges(session_id), self.loop
                )
            
        except Exception as e:
            logger.error(f"Error loading session exchanges: {e}")
    
    async def _async_load_session_exchanges(self, session_id: str):
        """Async method to load exchange data for a session."""
        try:
            session_data = await self.monitor.load_session_data(session_id)
            exchange_stats = session_data.get('exchange_stats', {})
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_exchanges_ui(exchange_stats))
            
        except Exception as e:
            logger.error(f"Error loading session exchanges: {e}")
            self.window.after(0, lambda: self._update_exchanges_error())
    
    def _update_exchanges_ui(self, exchange_stats: Dict[str, int]):
        """Update exchanges UI with loaded data."""
        try:
            self.exchange_listbox.delete(0, tk.END)
            
            if exchange_stats:
                # Sort exchanges by message count (descending)
                sorted_exchanges = sorted(exchange_stats.items(), key=lambda x: -x[1])
                
                for exchange_name, message_count in sorted_exchanges:
                    self.exchange_listbox.insert(
                        tk.END, f"{exchange_name} ({message_count:,} messages)"
                    )
            else:
                self.exchange_listbox.insert(tk.END, "No exchanges found")
                
        except Exception as e:
            logger.error(f"Error updating exchanges UI: {e}")
    
    def _update_exchanges_error(self):
        """Update exchanges UI with error message."""
        self.exchange_listbox.delete(0, tk.END)
        self.exchange_listbox.insert(tk.END, "Error loading exchanges")
    
    def _on_session_double_click(self, event):
        """Handle double-click on session to view data."""
        self._view_session_data()
    
    def _on_exchange_double_click(self, event):
        """Handle double-click on exchange to view messages."""
        selection = self.exchange_listbox.curselection()
        if not selection:
            return
            
        try:
            selected_session = self.session_tree.selection()
            if not selected_session:
                return
                
            session_id = self.session_tree.item(selected_session[0], "tags")[0]
            exchange_text = self.exchange_listbox.get(selection[0])
            
            if " (" in exchange_text:
                exchange_name = exchange_text.split(" (")[0]
            else:
                exchange_name = exchange_text
            
            if exchange_name not in ["Loading exchanges...", "No exchanges found", "Error loading exchanges"]:
                # Open session exchange viewer
                AsyncSessionExchangeViewerWindow(
                    self.window, session_id, exchange_name, self.monitor, self.loop
                )
            
        except Exception as e:
            logger.error(f"Error opening exchange viewer: {e}")
    
    def _view_session_data(self):
        """View detailed session data."""
        selection = self.session_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session first.")
            return
            
        try:
            item = selection[0]
            tags = self.session_tree.item(item, "tags")
            if not tags:
                return
                
            session_id = tags[0]
            session = self.sessions.get(session_id)
            
            if session:
                # Open session data viewer
                AsyncSessionDataViewerWindow(
                    self.window, session_id, session, self.monitor, self.loop
                )
                
        except Exception as e:
            logger.error(f"Error viewing session data: {e}")
            messagebox.showerror("Error", f"Failed to view session data: {e}")
    
    def _export_session(self):
        """Export session data."""
        selection = self.session_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session first.")
            return
            
        messagebox.showinfo("Export", "Export functionality to be implemented.")
    
    def _delete_session(self):
        """Delete selected session."""
        selection = self.session_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session first.")
            return
            
        try:
            item = selection[0]
            tags = self.session_tree.item(item, "tags")
            if not tags:
                return
                
            session_id = tags[0]
            session = self.sessions.get(session_id)
            
            if session:
                result = messagebox.askyesno(
                    "Delete Session", 
                    f"Are you sure you want to delete session '{session['name']}'?\n\n"
                    f"This will permanently remove all {session['total_messages']} messages "
                    f"and cannot be undone."
                )
                
                if result:
                    # Schedule async deletion
                    if self.loop:
                        future = asyncio.run_coroutine_threadsafe(
                            self._async_delete_session(session_id), self.loop
                        )
                    
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            messagebox.showerror("Error", f"Failed to delete session: {e}")
    
    async def _async_delete_session(self, session_id: str):
        """Async method to delete a session."""
        try:
            await self.monitor.delete_session(session_id)
            
            # Reload sessions on main thread
            self.window.after(0, self._load_sessions)
            self.window.after(0, lambda: messagebox.showinfo("Success", "Session deleted successfully"))
            
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to delete session: {e}"))


class AsyncSessionDataViewerWindow:
    """Async-compatible window for viewing detailed session data."""
    
    def __init__(self, parent, session_id: str, session: Dict, monitor, event_loop):
        self.parent = parent
        self.session_id = session_id
        self.session = session
        self.monitor = monitor
        self.loop = event_loop
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Session Data - {session['name']}")
        self.window.geometry("1200x800")
        
        self._setup_ui()
        self._load_session_data()
        
    def _setup_ui(self):
        """Setup the session data viewer UI."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text=f"📊 Session: {self.session['name']}",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header_frame,
            text="Refresh",
            command=self._load_session_data
        ).pack(side=tk.RIGHT)
        
        # Notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        self._setup_summary_tab()
        
        # Exchanges tab
        self.exchanges_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exchanges_frame, text="Exchanges")
        self._setup_exchanges_tab()
        
    def _setup_summary_tab(self):
        """Setup summary tab."""
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame, wrap=tk.WORD
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _setup_exchanges_tab(self):
        """Setup exchanges tab."""
        # Exchange list
        columns = ("Exchange", "Message Count")
        self.exchange_tree = ttk.Treeview(
            self.exchanges_frame, columns=columns, show="headings"
        )
        
        for col in columns:
            self.exchange_tree.heading(col, text=col)
            self.exchange_tree.column(col, width=300)
        
        # Scrollbar
        exchange_scrollbar = ttk.Scrollbar(
            self.exchanges_frame, orient=tk.VERTICAL, command=self.exchange_tree.yview
        )
        exchange_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exchange_tree.config(yscrollcommand=exchange_scrollbar.set)
        
        self.exchange_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.exchange_tree.bind('<Double-1>', self._on_exchange_double_click)
        
    def _load_session_data(self):
        """Load session data."""
        try:
            # Update summary immediately
            summary_text = f"""Session Summary
==============

Session Information:
- Name: {self.session['name']}
- ID: {self.session_id}
- Start Time: {self.session['start_time']}
- End Time: {self.session['end_time'] or 'Still Active'}
- Host: {self.session.get('host', 'Unknown')}
- Port: {self.session.get('port', 'Unknown')}
- Username: {self.session.get('username', 'Unknown')}
- Trace Queue: {self.session.get('trace_queue', 'Unknown')}

Statistics:
- Total Messages: {self.session['total_messages']:,}
- Unique Exchanges: {self.session['exchanges_count']}

Loading detailed data...
"""
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary_text)
            
            # Clear exchanges
            for item in self.exchange_tree.get_children():
                self.exchange_tree.delete(item)
                
            self.exchange_tree.insert('', tk.END, values=("Loading...", "..."))
            
            # Schedule async loading
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_load_session_data(), self.loop
                )
            
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
    
    async def _async_load_session_data(self):
        """Async method to load detailed session data."""
        try:
            session_data = await self.monitor.load_session_data(self.session_id)
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_session_data_ui(session_data))
            
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
            self.window.after(0, lambda: self._update_session_data_error(str(e)))
    
    def _update_session_data_ui(self, session_data: Dict):
        """Update UI with loaded session data."""
        try:
            exchange_stats = session_data.get('exchange_stats', {})
            messages = session_data.get('messages', [])
            
            # Update summary
            summary_text = f"""Session Summary
==============

Session Information:
- Name: {self.session['name']}
- ID: {self.session_id}
- Start Time: {self.session['start_time']}
- End Time: {self.session['end_time'] or 'Still Active'}
- Host: {self.session.get('host', 'Unknown')}
- Port: {self.session.get('port', 'Unknown')}
- Username: {self.session.get('username', 'Unknown')}
- Trace Queue: {self.session.get('trace_queue', 'Unknown')}

Statistics:
- Total Messages: {len(messages):,}
- Unique Exchanges: {len(exchange_stats)}

Recent Messages:
"""
            
            # Add recent messages preview
            for i, message in enumerate(messages[:10]):
                timestamp = message.get('timestamp', 'Unknown')
                exchange = message.get('exchange', 'Unknown')
                routing_key = message.get('routing_key', 'Unknown')
                
                summary_text += f"\n{i+1:2d}. {timestamp}\n"
                summary_text += f"    Exchange: {exchange}\n"
                summary_text += f"    Routing Key: {routing_key}\n"
            
            if len(messages) > 10:
                summary_text += f"\n... and {len(messages) - 10} more messages"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary_text)
            
            # Update exchanges
            for item in self.exchange_tree.get_children():
                self.exchange_tree.delete(item)
                
            sorted_exchanges = sorted(exchange_stats.items(), key=lambda x: -x[1])
            for exchange_name, message_count in sorted_exchanges:
                self.exchange_tree.insert(
                    '', tk.END,
                    values=(exchange_name, f"{message_count:,}"),
                    tags=(exchange_name,)
                )
                
        except Exception as e:
            logger.error(f"Error updating session data UI: {e}")
    
    def _update_session_data_error(self, error_msg: str):
        """Update UI with error message."""
        error_text = f"""Error Loading Session Data
========================

An error occurred while loading the session data:

{error_msg}

Please try refreshing or check the logs for more details.
"""
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, error_text)
        
        # Update exchanges
        for item in self.exchange_tree.get_children():
            self.exchange_tree.delete(item)
            
        self.exchange_tree.insert('', tk.END, values=("Error loading", "..."))
    
    def _on_exchange_double_click(self, event):
        """Handle double-click on exchange."""
        selection = self.exchange_tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            tags = self.exchange_tree.item(item, "tags")
            if not tags:
                return
                
            exchange_name = tags[0]
            
            if exchange_name not in ["Loading...", "Error loading"]:
                # Open exchange-specific viewer
                AsyncSessionExchangeViewerWindow(
                    self.window, self.session_id, exchange_name, self.monitor, self.loop
                )
                
        except Exception as e:
            logger.error(f"Error opening exchange viewer: {e}")


class AsyncSessionExchangeViewerWindow:
    """Async-compatible window for viewing messages from a specific exchange in a session."""
    
    def __init__(self, parent, session_id: str, exchange_name: str, monitor, event_loop):
        self.parent = parent
        self.session_id = session_id
        self.exchange_name = exchange_name
        self.monitor = monitor
        self.loop = event_loop
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Session Exchange - {exchange_name}")
        self.window.geometry("1000x700")
        
        self._setup_ui()
        self._load_exchange_data()
        
    def _setup_ui(self):
        """Setup the exchange viewer UI."""
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
        
        ttk.Button(
            header_frame,
            text="Refresh",
            command=self._load_exchange_data
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            header_frame,
            text="Export All Messages as JSON",
            command=self._export_all_messages
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            header_frame,
            text="Export Routing Key as JSON",
            command=self._export_routing_key_messages
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Split view: Routing keys on left, messages on right
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Routing keys
        left_frame = ttk.LabelFrame(paned_window, text="Routing Keys")
        paned_window.add(left_frame, weight=1)
        
        self.routing_key_listbox = tk.Listbox(left_frame)
        self.routing_key_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.routing_key_listbox.bind('<Double-1>', self._on_routing_key_double_click)
        self.routing_key_listbox.bind('<<ListboxSelect>>', self._on_routing_key_select)
        
        # Right panel: Messages
        right_frame = ttk.LabelFrame(paned_window, text="Messages")
        paned_window.add(right_frame, weight=2)
        
        self.messages_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _load_exchange_data(self):
        """Load exchange data."""
        try:
            # Clear current data
            self.routing_key_listbox.delete(0, tk.END)
            self.routing_key_listbox.insert(tk.END, "Loading routing keys...")
            
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, f"Loading messages for exchange '{self.exchange_name}'...")
            
            # Schedule async loading
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_load_exchange_data(), self.loop
                )
            
        except Exception as e:
            logger.error(f"Error loading exchange data: {e}")
    
    async def _async_load_exchange_data(self):
        """Async method to load exchange data."""
        try:
            routing_keys = await self.monitor.get_session_routing_keys(
                self.session_id, self.exchange_name
            )
            messages = await self.monitor.get_session_exchange_messages(
                self.session_id, self.exchange_name, limit=100
            )
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_exchange_data_ui(routing_keys, messages))
            
        except Exception as e:
            logger.error(f"Error loading exchange data: {e}")
            self.window.after(0, lambda: self._update_exchange_data_error(str(e)))
    
    def _update_exchange_data_ui(self, routing_keys: List[str], messages: List[Dict]):
        """Update UI with loaded exchange data."""
        try:
            # Update routing keys
            self.routing_key_listbox.delete(0, tk.END)
            
            if routing_keys:
                for routing_key in routing_keys:
                    self.routing_key_listbox.insert(tk.END, routing_key)
            else:
                self.routing_key_listbox.insert(tk.END, "No routing keys found")
            
            # Update messages
            messages_text = f"Messages for Exchange: {self.exchange_name}\n"
            messages_text += "=" * 50 + "\n\n"
            messages_text += f"Total Messages: {len(messages)}\n\n"
            
            for i, message in enumerate(messages[:20]):  # Show first 20
                timestamp = message.get('timestamp', 'Unknown')
                routing_key = message.get('routing_key', 'Unknown')
                trace_type = message.get('trace_type', 'Unknown')
                
                messages_text += f"{i+1:2d}. {timestamp}\n"
                messages_text += f"    Routing Key: {routing_key}\n"
                messages_text += f"    Trace Type: {trace_type}\n"
                messages_text += "-" * 30 + "\n"
            
            if len(messages) > 20:
                messages_text += f"\n... and {len(messages) - 20} more messages"
            
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, messages_text)
            
        except Exception as e:
            logger.error(f"Error updating exchange data UI: {e}")
    
    def _update_exchange_data_error(self, error_msg: str):
        """Update UI with error message."""
        self.routing_key_listbox.delete(0, tk.END)
        self.routing_key_listbox.insert(tk.END, "Error loading routing keys")
        
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.insert(1.0, f"Error loading exchange data:\n\n{error_msg}")
    
    def _on_routing_key_select(self, event):
        """Handle routing key selection."""
        selection = self.routing_key_listbox.curselection()
        if not selection:
            return
            
        try:
            routing_key = self.routing_key_listbox.get(selection[0])
            
            if routing_key not in ["Loading routing keys...", "No routing keys found", "Error loading routing keys"]:
                # Load messages for this routing key
                self._load_routing_key_messages(routing_key)
                
        except Exception as e:
            logger.error(f"Error selecting routing key: {e}")
    
    def _on_routing_key_double_click(self, event):
        """Handle double-click on routing key."""
        # Same as select for now
        self._on_routing_key_select(event)
    
    def _load_routing_key_messages(self, routing_key: str):
        """Load messages for a specific routing key."""
        try:
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, f"Loading messages for routing key: {routing_key}...")
            
            # Schedule async loading
            if self.loop:
                future = asyncio.run_coroutine_threadsafe(
                    self._async_load_routing_key_messages(routing_key), self.loop
                )
            
        except Exception as e:
            logger.error(f"Error loading routing key messages: {e}")
    
    async def _async_load_routing_key_messages(self, routing_key: str):
        """Async method to load messages for a routing key."""
        try:
            messages = await self.monitor.get_session_routing_key_messages(
                self.session_id, self.exchange_name, routing_key, limit=50
            )
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_routing_key_messages_ui(routing_key, messages))
            
        except Exception as e:
            logger.error(f"Error loading routing key messages: {e}")
            self.window.after(0, lambda: self._update_routing_key_messages_error(routing_key, str(e)))
    
    def _update_routing_key_messages_ui(self, routing_key: str, messages: List[Dict]):
        """Update UI with routing key messages."""
        try:
            messages_text = f"Messages for Routing Key: {routing_key}\n"
            messages_text += "=" * 50 + "\n\n"
            messages_text += f"Exchange: {self.exchange_name}\n"
            messages_text += f"Total Messages: {len(messages)}\n\n"
            
            for i, message in enumerate(messages):
                timestamp = message.get('timestamp', 'Unknown')
                trace_type = message.get('trace_type', 'Unknown')
                body = message.get('body', {})
                
                messages_text += f"{i+1:2d}. {timestamp}\n"
                messages_text += f"    Trace Type: {trace_type}\n"
                
                if body:
                    # Show first few lines of body
                    body_str = json.dumps(body, indent=2)
                    body_lines = body_str.split('\n')[:5]  # First 5 lines
                    messages_text += f"    Body: {body_lines[0]}\n"
                    for line in body_lines[1:]:
                        messages_text += f"          {line}\n"
                    if len(body_str.split('\n')) > 5:
                        messages_text += "          ...\n"
                
                messages_text += "-" * 40 + "\n"
            
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, messages_text)
            
        except Exception as e:
            logger.error(f"Error updating routing key messages UI: {e}")
    
    def _update_routing_key_messages_error(self, routing_key: str, error_msg: str):
        """Update UI with routing key messages error."""
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.insert(1.0, f"Error loading messages for routing key '{routing_key}':\n\n{error_msg}")
    
    def _export_all_messages(self):
        """Export all messages for the exchange as JSON."""
        try:
            # Get current timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"exchange_{self.exchange_name}_{timestamp}.json"
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Export Exchange Messages",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                # Load all messages for this exchange
                if self.loop:
                    future = asyncio.run_coroutine_threadsafe(
                        self._async_export_all_messages(file_path), self.loop
                    )
                
        except Exception as e:
            logger.error(f"Error starting export: {e}")
            messagebox.showerror("Export Error", f"Failed to start export: {e}")
    
    def _export_routing_key_messages(self):
        """Export messages for currently selected routing key as JSON."""
        selection = self.routing_key_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a routing key first.")
            return
            
        try:
            routing_key = self.routing_key_listbox.get(selection[0])
            
            if routing_key in ["Loading routing keys...", "No routing keys found", "Error loading routing keys"]:
                messagebox.showwarning("Invalid Selection", "Please select a valid routing key.")
                return
            
            # Get current timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"routing_key_{self.exchange_name}_{routing_key}_{timestamp}.json"
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title=f"Export Routing Key Messages ({routing_key})",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                # Load messages for this routing key
                if self.loop:
                    future = asyncio.run_coroutine_threadsafe(
                        self._async_export_routing_key_messages(file_path, routing_key), self.loop
                    )
                
        except Exception as e:
            logger.error(f"Error starting routing key export: {e}")
            messagebox.showerror("Export Error", f"Failed to start export: {e}")
    
    async def _async_export_all_messages(self, file_path: str):
        """Async method to export all exchange messages."""
        try:
            # Get all messages for this exchange
            messages = await self.monitor.get_session_exchange_messages(
                self.session_id, self.exchange_name, limit=10000  # Large limit to get all
            )
            
            # Prepare export data
            export_data = {
                "export_info": {
                    "session_id": self.session_id,
                    "exchange_name": self.exchange_name,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_messages": len(messages)
                },
                "messages": messages
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            # Show success message on main thread
            self.window.after(0, lambda: messagebox.showinfo(
                "Export Successful", 
                f"Exported {len(messages)} messages to {file_path}"
            ))
            
        except Exception as e:
            logger.error(f"Error exporting messages: {e}")
            self.window.after(0, lambda: messagebox.showerror(
                "Export Error", f"Failed to export messages: {e}"
            ))
    
    async def _async_export_routing_key_messages(self, file_path: str, routing_key: str):
        """Async method to export routing key messages."""
        try:
            # Get messages for this routing key
            messages = await self.monitor.get_session_routing_key_messages(
                self.session_id, self.exchange_name, routing_key, limit=10000  # Large limit
            )
            
            # Prepare export data
            export_data = {
                "export_info": {
                    "session_id": self.session_id,
                    "exchange_name": self.exchange_name,
                    "routing_key": routing_key,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_messages": len(messages)
                },
                "messages": messages
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            # Show success message on main thread
            self.window.after(0, lambda: messagebox.showinfo(
                "Export Successful", 
                f"Exported {len(messages)} messages for routing key '{routing_key}' to {file_path}"
            ))
            
        except Exception as e:
            logger.error(f"Error exporting routing key messages: {e}")
            self.window.after(0, lambda: messagebox.showerror(
                "Export Error", f"Failed to export routing key messages: {e}"
            ))