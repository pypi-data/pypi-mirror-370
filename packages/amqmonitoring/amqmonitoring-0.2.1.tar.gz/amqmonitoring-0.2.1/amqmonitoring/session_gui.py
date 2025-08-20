#!/usr/bin/env python3
"""
Session management GUI components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SessionListWindow:
    """Window for managing monitoring sessions."""
    
    def __init__(self, parent, monitor):
        self.parent = parent
        self.monitor = monitor
        
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
        """Load sessions from database."""
        try:
            # This is a placeholder - in a real implementation, this would need
            # to be called asynchronously from the GUI's event loop
            # For now, we'll show a loading message
            
            # Clear current items
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
                
            # Add loading indicator
            self.session_tree.insert(
                '', tk.END,
                values=("Loading...", "...", "...", "...", "...")
            )
            
            # In a production version, you would:
            # 1. Get the GUI's async event loop
            # 2. Schedule the async call
            # 3. Update the UI when the data arrives
            
            logger.info("Session loading placeholder - async implementation needed")
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            messagebox.showerror("Error", f"Failed to load sessions: {e}")
            
        # Old async implementation (commented for reference):
        """
        try:
            sessions = await self.monitor.get_sessions(limit=100)
            
            # Clear current items
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
            logger.error(f"Error loading sessions: {e}")
            messagebox.showerror("Error", f"Failed to load sessions: {e}")
        """
    
    def _on_session_select(self, event):
        """Handle session selection."""
        selection = self.session_tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            session_id = self.session_tree.item(item, "tags")[0]
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
            # This would need to be implemented as an async call
            # For now, clear the list
            self.exchange_listbox.delete(0, tk.END)
            self.exchange_listbox.insert(tk.END, "Loading exchanges...")
            
            # In a real implementation, you'd call an async method here
            # and update the UI when the data is ready
            
        except Exception as e:
            logger.error(f"Error loading session exchanges: {e}")
    
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
            exchange_name = self.exchange_listbox.get(selection[0])
            
            # Open session exchange viewer
            SessionExchangeViewerWindow(
                self.window, session_id, exchange_name, self.monitor
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
            session_id = self.session_tree.item(item, "tags")[0]
            session = self.sessions.get(session_id)
            
            if session:
                # Open session data viewer
                SessionDataViewerWindow(self.window, session_id, session, self.monitor)
                
        except Exception as e:
            logger.error(f"Error viewing session data: {e}")
            messagebox.showerror("Error", f"Failed to view session data: {e}")
    
    def _export_session(self):
        """Export session data."""
        selection = self.session_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session first.")
            return
            
        messagebox.showinfo("Export", "Export functionality not yet implemented.")
    
    def _delete_session(self):
        """Delete selected session."""
        selection = self.session_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session first.")
            return
            
        try:
            item = selection[0]
            session_id = self.session_tree.item(item, "tags")[0]
            session = self.sessions.get(session_id)
            
            if session:
                result = messagebox.askyesno(
                    "Delete Session", 
                    f"Are you sure you want to delete session '{session['name']}'?\n\n"
                    f"This will permanently remove all {session['total_messages']} messages "
                    f"and cannot be undone."
                )
                
                if result:
                    # This would need to be implemented as an async call
                    messagebox.showinfo("Delete", "Delete functionality not yet fully implemented.")
                    
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            messagebox.showerror("Error", f"Failed to delete session: {e}")


class SessionDataViewerWindow:
    """Window for viewing detailed session data."""
    
    def __init__(self, parent, session_id: str, session: Dict, monitor):
        self.parent = parent
        self.session_id = session_id
        self.session = session
        self.monitor = monitor
        
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
        
        # Exchanges tab
        self.exchanges_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exchanges_frame, text="Exchanges")
        self._setup_exchanges_tab()
        
        # Messages tab
        self.messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messages_frame, text="All Messages")
        self._setup_messages_tab()
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        self._setup_summary_tab()
        
    def _setup_exchanges_tab(self):
        """Setup exchanges tab."""
        # Exchange list
        columns = ("Exchange", "Message Count", "Routing Keys")
        self.exchange_tree = ttk.Treeview(
            self.exchanges_frame, columns=columns, show="headings"
        )
        
        for col in columns:
            self.exchange_tree.heading(col, text=col)
            self.exchange_tree.column(col, width=200)
        
        # Scrollbar
        exchange_scrollbar = ttk.Scrollbar(
            self.exchanges_frame, orient=tk.VERTICAL, command=self.exchange_tree.yview
        )
        exchange_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exchange_tree.config(yscrollcommand=exchange_scrollbar.set)
        
        self.exchange_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.exchange_tree.bind('<Double-1>', self._on_exchange_double_click)
        
    def _setup_messages_tab(self):
        """Setup messages tab."""
        # Messages list
        self.messages_text = scrolledtext.ScrolledText(
            self.messages_frame, wrap=tk.WORD
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _setup_summary_tab(self):
        """Setup summary tab."""
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame, wrap=tk.WORD
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _load_session_data(self):
        """Load session data (placeholder for async implementation)."""
        try:
            # In a real implementation, this would make async calls to load data
            
            # Load summary
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

This session data viewer shows a placeholder implementation.
Full async data loading would be implemented in a production version.
"""
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary_text)
            
            # Placeholder for exchanges
            self.exchange_tree.insert(
                '', tk.END,
                values=("Loading...", "...", "...")
            )
            
            # Placeholder for messages
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, "Loading session messages...")
            
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
    
    def _on_exchange_double_click(self, event):
        """Handle double-click on exchange."""
        selection = self.exchange_tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            exchange_name = self.exchange_tree.item(item, "values")[0]
            
            if exchange_name != "Loading...":
                # Open exchange-specific viewer
                SessionExchangeViewerWindow(
                    self.window, self.session_id, exchange_name, self.monitor
                )
                
        except Exception as e:
            logger.error(f"Error opening exchange viewer: {e}")


class SessionExchangeViewerWindow:
    """Window for viewing messages from a specific exchange in a session."""
    
    def __init__(self, parent, session_id: str, exchange_name: str, monitor):
        self.parent = parent
        self.session_id = session_id
        self.exchange_name = exchange_name
        self.monitor = monitor
        
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
        
        # Split view: Routing keys on left, messages on right
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Routing keys
        left_frame = ttk.LabelFrame(paned_window, text="Routing Keys")
        paned_window.add(left_frame, weight=1)
        
        self.routing_key_listbox = tk.Listbox(left_frame)
        self.routing_key_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.routing_key_listbox.bind('<Double-1>', self._on_routing_key_double_click)
        
        # Right panel: Messages
        right_frame = ttk.LabelFrame(paned_window, text="Messages")
        paned_window.add(right_frame, weight=2)
        
        self.messages_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _load_exchange_data(self):
        """Load exchange data (placeholder)."""
        try:
            # Placeholder implementation
            self.routing_key_listbox.delete(0, tk.END)
            self.routing_key_listbox.insert(tk.END, "Loading routing keys...")
            
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(1.0, f"Loading messages for exchange '{self.exchange_name}' from session...")
            
        except Exception as e:
            logger.error(f"Error loading exchange data: {e}")
    
    def _on_routing_key_double_click(self, event):
        """Handle double-click on routing key."""
        selection = self.routing_key_listbox.curselection()
        if not selection:
            return
            
        try:
            routing_key = self.routing_key_listbox.get(selection[0])
            
            if routing_key != "Loading routing keys...":
                # Show messages for this routing key
                self.messages_text.delete(1.0, tk.END)
                self.messages_text.insert(1.0, f"Messages for routing key: {routing_key}\n\nLoading...")
                
        except Exception as e:
            logger.error(f"Error loading routing key messages: {e}")


def start_session_if_needed(monitor, gui_interface):
    """Start a new session when connecting if none is active."""
    try:
        if not monitor.session_manager.is_session_active():
            # Create session name based on connection info
            session_name = f"{monitor.host}_{monitor.port}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # This would be called from the GUI's async connect method
            # For now, this is a placeholder
            logger.info(f"Would start session: {session_name}")
            
    except Exception as e:
        logger.error(f"Error starting session: {e}")