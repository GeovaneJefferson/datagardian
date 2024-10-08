import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from server import *
from device_location import device_location

server = SERVER()

# BUG
# In auto select backup, is auto selecting the first users backup device.

class UIWindow(Adw.PreferencesWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ##########################################################################
        # WINDOW
        ##########################################################################
        # Create a Preferences Window with tabs
        self.set_title("Settings")
        self.set_size_request(600, 400)
        self.set_resizable(False)  # Prevent window from being resized

        self.setup_preferences_pages()

        # Load available devices
        self.available_devices_location()

        # Auto-select the backup device based on saved configuration
        self.auto_select_backup_device()

        # Auto-select 'Backup Automatically'
        self.auto_select_auto_backup()

    def setup_preferences_pages(self):
        # Setting up the preferences pages...
        ##########################################################################
        # PAGES - General
        ##########################################################################
        # General Tab
        general_page = Adw.PreferencesPage()
        # general_page.set_icon_name("folder-open-symbolic")

        # General Tab
        general_page = Adw.PreferencesPage()
        general_group = Adw.PreferencesGroup(title="Storage")

        # Location (ComboBox for backup location)
        self.location_row = Adw.ComboRow(title="Location", selected=0)
        self.location_row.set_model(Gtk.StringList.new(["Local Folder"]))
        self.location_row.connect("notify::selected", self.on_location_changed)

        # Folder button
        folder_button = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        folder_button.set_tooltip_text("Select folder")
        folder_button.connect("clicked", self.on_folder_button_clicked)

        # Create box to hold folder button
        folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        folder_box.append(folder_button)
        folder_box.set_sensitive(False)
        self.location_row.add_suffix(folder_box)

        # Backup Device (Expandable Row)
        self.backup_device_row = Adw.ExpanderRow(title="Backup Device")
        self.backup_device_list = Gtk.ComboBoxText()
        self.backup_device_list.set_id_column(0)
        self.backup_device_list.connect("changed", self.on_backup_device_selected)  # Connect the signal
        self.backup_device_row.add_row(self.backup_device_list)
        # self.backup_device_row.add_suffix(refresh_button)

        general_group.add(self.location_row)
        general_group.add(self.backup_device_row)
        general_page.add(general_group)

        ##########################################################################
        # PAGES - GENERAL - SCHEDULE
        ##########################################################################
        # Schedule section
        schedule_group = Adw.PreferencesGroup(title="Real-time protection")

        # Backup Automation Switch
        self.switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Create a label for the switch with your specified text
        label = Gtk.Label(label="   Back up new and changed files in your home.")

        # Create the switch
        self.programmatic_change = False  # Add this line
        self.auto_backup_switch = Gtk.Switch()
        # self.auto_backup_switch.set_tooltip_text('Coming soon...')
        self.auto_backup_switch.connect("notify::active", self.on_auto_backup_switch_toggled)

        # Add the label to the switch box
        self.switch_box.append(self.auto_backup_switch)
        self.switch_box.append(label)

        ######################################################################
        # Add groups
        schedule_group.add(self.switch_box)
        # Schedule groups
        general_page.add(schedule_group)
        # Adding General page to PreferencesWindow
        self.add(general_page)

        ##########################################################################
        # PAGES - FOLDERS - FOLDER TO IGNORE
        ##########################################################################
        # Folders Tab
        folders_page = Adw.PreferencesPage()
        # folders_page.set_icon_name("folder-open-symbolic")
        self.add(folders_page)

        # Create the groups
        ignore_group = Adw.PreferencesGroup(title="Folders to ignore")
        exclude_group = Adw.PreferencesGroup(title="Exclude")

        # Add folder selector to ignore
        folder_select_button = Gtk.Button(label="Add Folder")
        folder_select_button.connect("clicked", self.on_folder_select_button_clicked)
        ignore_group.add(folder_select_button)

        # Backup Automation Switch
        hidden_switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Create a label for the switch
        label = Gtk.Label(label="   Ignore hidden files and empty folders.")

        # Create the switch
        self.ignore_hidden_switch = Gtk.Switch()
        self.ignore_hidden_switch.connect("notify::active", self.on_auto_backup_switch_toggled)

        # Add the label to the switch box
        hidden_switch_box.append(self.ignore_hidden_switch)
        hidden_switch_box.append(label)

        # Add the switch box to the exclude group
        exclude_group.add(hidden_switch_box)

        # Add groups to folders_page
        folders_page.add(exclude_group)
        folders_page.add(ignore_group)

        # Set titles for tabs
        general_page.set_title("General")
        folders_page.set_title("Folders")

    def on_ignore_hidden_switch_toggled(self, switch, gparam):
        # Handle the toggle state of the ignore hidden switch
        if switch.get_active():
            print("Ignoring hidden files and folders.")
            # Add logic to handle ignoring hidden files/folders
        else:
            print("Not ignoring hidden files and folders.")
            # Add logic to revert this behavior

    def auto_select_backup_device(self):
        # Get stored driver_location and driver_name
        driver_location = server.get_database_value(
            section='DRIVER',
            option='driver_location')

        driver_name = server.get_database_value(
            section='DRIVER',
            option='driver_name')

        # Automatically select the registered device
        if driver_name and driver_location:
            # Iterate over the items in the ComboBoxText to find the index of the device
            model = self.backup_device_list.get_model()
            for i, item in enumerate(model):
                if item[0] == driver_name:  # Use index 0 to access the item text
                    self.backup_device_list.set_active(i)
                    break

    def auto_select_auto_backup(self):
        # Get stored driver_location and driver_name
        automatically_backup = server.get_database_value(
            section='BACKUP',
            option='automatically_backup')

        self.programmatic_change = True  # Set the flag to indicate programmatic change

        if automatically_backup:
            self.auto_backup_switch.set_active(True)
        else:
            self.auto_backup_switch.set_active(False)
        
        self.programmatic_change = False  # Reset the flag after programmatic change

    def on_location_changed(self, combo_row, pspec):
        # Handle location changes
        self.available_devices_location()  # Refresh devices list based on selected location

    def on_folder_button_clicked(self, button):
        # Handle folder button click
        print("Folder button clicked")
        # Open a file chooser dialog if needed

    def on_auto_backup_switch_toggled(self, switch, pspec):
        if self.programmatic_change:
            return  # Exit the function if it's a programmatic change

        # Handle system tray switch toggling
        auto_backup_active = switch.get_active()
        true_false: str = 'false'

        if auto_backup_active:
            if not server.is_daemon_running():
                self.start_daemon()  # Only start if not running
            true_false = 'true'
            self.create_autostart_entry()  # Create .desktop file for auto startup
        else:
            self.stop_daemon()  # Stop the daemon
            self.remove_autostart_entry()  # Optionally remove autostart entry

        # Update the conf file
        server.set_database_value(
            section='BACKUP',
            option='automatically_backup',
            value=true_false)

    def create_autostart_entry(self):
        autostart_dir = os.path.expanduser("~/.config/autostart/")
        os.makedirs(autostart_dir, exist_ok=True)

        desktop_file_content = f"""
            [Desktop Entry]
            Type=Application
            Exec=flatpak run --command=python3 {server.ID} /app/share/dataguardian/src/at_boot.py
            X-GNOME-Autostart-enabled=true
            Name={server.APP_NAME}
            Comment[en_US]=Automatically start {server.APP_NAME}
            Comment=Automatically start {server.APP_NAME}
            """

        with open(os.path.join(autostart_dir, f"{server.APP_NAME_CLOSE_LOWER}_autostart.desktop"), 'w') as f:
            f.write(desktop_file_content)
        logging.info("Autostart entry created.")

    def remove_autostart_entry(self):
        autostart_file = os.path.expanduser(f"~/.config/autostart/{server.APP_NAME.lower()}_autostart.desktop")
        if os.path.exists(autostart_file):
            os.remove(autostart_file)
            logging.info("Autostart entry removed.")

    def start_daemon(self):
        """Start the daemon and store its PID, ensuring only one instance runs."""
        # Start a new daemon process
        process = sub.Popen(['python3', server.DAEMON_PY_LOCATION], start_new_session=True)

        # Store the new PID in the file
        with open(server.DAEMON_PID_LOCATION, 'w') as f:
            f.write(str(process.pid))
        print(f"Daemon started with PID {process.pid}.")

    def stop_daemon(self):
        """Stop the daemon by reading its PID."""
        if os.path.exists(server.DAEMON_PID_LOCATION):
            with open(server.DAEMON_PID_LOCATION, 'r') as f:
                pid = int(f.read())

            try:
                os.kill(pid, signal.SIGTERM)  # Send termination signal
                os.waitpid(pid, 0)  # Wait for the process to terminate
                os.remove(server.DAEMON_PID_LOCATION)
                print(f"Daemon with PID {pid} stopped.")
            except OSError as e:
                print(f"Failed to stop daemon with PID {pid}. Error: {e}")
                if e.errno == errno.ESRCH:
                    print(f"Daemon with PID {pid} not found. Removing stale PID file.")
                    os.remove(server.DAEMON_PID_LOCATION)
        else:
            print("Daemon is not running.")

    def on_folder_select_button_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select a Folder To Ignore",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )

        # Set the transient parent to ensure proper behavior
        dialog.set_transient_for(self)

        # Add buttons for the dialog
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.OK)

        dialog.connect("response", self.on_filechooser_response)

        dialog.present()

    def on_filechooser_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            selected_folder = dialog.get_file()
            
            if selected_folder is not None:
                selected_folder = selected_folder.get_path()
                
                print(f"Selected folder: {selected_folder}")

                # Convert the selected folder to a relative path
                rel_path = os.path.relpath(selected_folder, server.USER_HOME)  # Adjust based on the base directory
                
                print(f"Selected folder rel: {rel_path}")

                # Add the relative path to the config file
                self.add_folder_to_config(rel_path)

        dialog.destroy()

    def add_folder_to_config(self, folder):
        config_file_path = 'src/database/config.conf'  # Adjust to the actual path of your config file

        # Read the current config file content
        with open(config_file_path, 'r') as file:
            lines = file.readlines()

        # Look for the [EXCLUDE_FOLDER] section
        exclude_section_found = False
        for i, line in enumerate(lines):
            if line.strip() == "[EXCLUDE_FOLDER]":
                exclude_section_found = True
            elif exclude_section_found and line.strip() == "":
                # Add the new folder just before the next empty line
                lines.insert(i, f"{folder}\n")  # Ensure there's a newline before the folder
                break

        # If the section is not found, append it at the end
        if not exclude_section_found:
            lines.append("\n[EXCLUDE_FOLDER]\n")  # Add the section header if not found
            lines.append(f"{folder}\n")  # Add the folder with a newline

        # If the section was found but no empty line was encountered, add it at the end
        elif exclude_section_found and lines[-1].strip() != "":
            lines.append(f"{folder}\n")  # Add the folder to the end

        # Write back the updated content to the config file
        with open(config_file_path, 'w') as file:
            file.writelines(lines)

        print(f"Added folder to config: {folder}")  # For debugging

    def on_backup_device_selected(self, combo_box):
        # Handle backup device selection
        selected_device = combo_box.get_active_text()
        driver_location = f"{device_location()}/{SERVER().USERNAME}/{selected_device}"

        # Update and add the device to the conf file
        # Devices location
        server.set_database_value(
			section='DRIVER',
			option='driver_location',
			value=str(driver_location)
        )

        # Devices name
        server.set_database_value(
            section='DRIVER',
            option='driver_name',
            value=str(selected_device)
        )

    def available_devices_location(self, button=None):
        location = device_location()  # Get backup device location. /media or /run

        if location:
            try:
                # Clear previous device items from the ComboBox
                self.backup_device_list.remove_all()

                # Iterate over the external devices and add them to the list
                for backup_device in os.listdir(f'{location}/{SERVER().USERNAME}'):
                    # if "'" not in backup_device and " " not in backup_device:
                    self.backup_device_list.append_text(backup_device)

            except FileNotFoundError:
                print(f"Path {location}/{SERVER().USERNAME} does not exist or cannot be accessed.")
        else:
            print("No devices found.")

        return True  # Keep the timeout running


if __name__ == '__main__':
    app = Adw.Application()
    win = UIWindow(application=app)
    app.run()