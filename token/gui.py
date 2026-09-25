import customtkinter as ctk
from spotify_client import spotify_handler
from esp32_client import esp32_handler

# -- GUI appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

import customtkinter as ctk

# -- Custom Labeled Entry
class LabeledEntry(ctk.CTkFrame):
    # -- Init class
    def __init__(self,
                    master,
                    label_text="",
                    placeholder_text="",
                    corner_radius=8,
                    **kwargs,
                ):

        # -- Transparent background
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)

        # -- Label
        self.label = ctk.CTkLabel(self, text=label_text, corner_radius=corner_radius)
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # -- Entry
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder_text, corner_radius=corner_radius)
        self.entry.grid(row=0, column=1, sticky="ew")

    # -- Get method
    def get(self):
        return self.entry.get()

    # -- Delete method
    def delete(self, first_index=0, last_index="end"):
        self.entry.delete(first_index, last_index)

    # -- Destroy method
    def destroy(self):
        self.label.destroy()
        self.entry.destroy()

# -- GUI class
class spotify_app(ctk.CTk):
    # -- Init class
    def __init__(self):
        super().__init__()

        # -- Spotify handler
        self.spotify = spotify_handler()
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.redirected_url = None

        # ESP32 handler
        self.esp32 = esp32_handler()
        self.client_id_send = None
        self.client_secret_send = None
        self.redirect_uri_send = None
        self.refresh_token_send = None
        self.esp32_ip = None
        self.esp32_port = None

        # -- Main
        self.title("Spotify ESP32-S3")
        self.geometry("450x420")
        self.title_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.btn_font = ctk.CTkFont(size=13, weight="bold")

        # -- Tabview container
        self.tabview = ctk.CTkTabview(self, width=300, height=400)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # -- Token auth tab
        self.tabview.add("Refresh Token")

        # -- Token remote tab
        self.tabview.add("Change credentials remotely")

        self.build_refresh_token_tab()
        self.build_change_credentials_remotely_tab()

    # -- Build authentication token
    def build_refresh_token_tab(self):
        # -- Authentication token tab
        self.refresh_token_tab = self.tabview.tab("Refresh Token")
        self.refresh_token_tab.grid_columnconfigure(0, weight=1)

        # -- Auth label text
        self.refresh_token_tab_label = ctk.CTkLabel(
            master=self.refresh_token_tab,
            text="Go to spotify for developers to get your credentials",
            corner_radius=8
        )
        self.refresh_token_tab_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Client ID entry
        self.client_id_entry = LabeledEntry(
            master=self.refresh_token_tab,
            label_text="Client ID",
            placeholder_text="Enter Client ID",
        )
        self.client_id_entry.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew"
        )

        # -- Client Secret entry
        self.client_secret_entry = LabeledEntry(
            master=self.refresh_token_tab,
            label_text="Client Secret",
            placeholder_text="Enter Client Secret",
        )
        self.client_secret_entry.grid(row=2, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Redirect URI entry
        self.redirect_uri_entry = LabeledEntry(
            master=self.refresh_token_tab,
            label_text="Redirect URI",
            placeholder_text="Enter Redirect URI",
        )
        self.redirect_uri_entry.grid(row=3, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Enter credentials button
        self.enter_credentials_button = ctk.CTkButton(
            master=self.refresh_token_tab,
            text="Enter credentials",
            command=self.enter_credentials_token
        )
        self.enter_credentials_button.grid(row=4, column=0, padx=10, pady=10)

    # -- Get authentication token
    def enter_credentials_token(self):
        # Get all credentials from entries
        self.client_id = self.client_id_entry.get().strip() or None
        self.client_secret = self.client_secret_entry.get().strip() or None
        self.redirect_uri = self.redirect_uri_entry.get().strip() or None

        # No entries shall be empty
        if self.client_id and self.client_secret and self.redirect_uri:
            # Create dict for pass env
            env_key = {
                "CLIENT_ID": self.client_id,
                "CLIENT_SECRET": self.client_secret,
                "REDIRECT_URI": self.redirect_uri
            }

            # Create .env or update existing env
            self.spotify.env_handler(env_key=env_key)

            # Authenticate url
            self.spotify.auth_url()

            # Delete widgets
            self.client_id_entry.destroy()
            self.client_secret_entry.destroy()
            self.redirect_uri_entry.destroy()
            self.enter_credentials_button.destroy()
            self.refresh_token_tab_label.destroy()

            # -- Redirected URL entry
            self.redirected_url_entry = ctk.CTkEntry(
                master=self.refresh_token_tab,
                placeholder_text="Enter the Redirected URL",
                corner_radius=8
            )
            self.redirected_url_entry.grid(row=1, column=0, padx=10, pady=(20, 10), sticky="ew")

            # -- Get refresh token button
            self.get_refresh_token_button = ctk.CTkButton(
                master=self.refresh_token_tab,
                text="Get refresh token",
                command=self.get_refresh_token
            )
            self.get_refresh_token_button.grid(row=2, column=0, padx=10, pady=10)

        else:
            print("Some entry is empty...")

    def get_refresh_token(self):
        # Gets redirected url from entry
        self.redirected_url = self.redirected_url_entry.get()

        # If redirected url is not empty
        if self.redirected_url:
            # Destroy widgets
            self.redirected_url_entry.destroy()
            self.get_refresh_token_button.destroy()

            # Try to get refresh token
            try:
                # Refresh token
                self.spotify.get_tokens(redirect_url=self.redirected_url)
                print(self.spotify.refresh_token)

                # -- Refresh token label
                self.refresh_token_label = ctk.CTkLabel(
                    master=self.refresh_token_tab,
                    text=f"Refresh token: \n{self.spotify.refresh_token}",
                    corner_radius=8
                )
                self.refresh_token_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

                # -- Get refresh token button
                self.copy_to_clipboard_button = ctk.CTkButton(
                    master=self.refresh_token_tab,
                    text="Copy to clipboard",
                    command=lambda:self.copy_to_clipboard(self.spotify.refresh_token)
                )
                self.copy_to_clipboard_button.grid(row=1, column=0, padx=10, pady=10)

            except Exception as e:
                # -- Something went wrong, error
                error_label = ctk.CTkLabel(
                    master=self.refresh_token_tab,
                    text=f"Something went wrong :(\nPlease check your credentials\nError: {e}",
                    corner_radius=8
                )
                error_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

        # Redirected url is empty
        else:
            print("Redirected url is empty")

    # -- Copy to clipboard
    def copy_to_clipboard(self, entry):
        # -- Clear current system clipboard
        self.clipboard_clear()
        # -- Append new text to clipboard
        self.clipboard_append(entry)

    # -- Build the sent cr
    def build_change_credentials_remotely_tab(self):
        self.change_credentials_remotely_tab = self.tabview.tab("Change credentials remotely")
        self.change_credentials_remotely_tab.grid_columnconfigure(0, weight=1)

        # -- Label for tab
        self.change_credentials_remotely_label = ctk.CTkLabel(
            master=self.change_credentials_remotely_tab,
            text="Enter the credentials that will be sent to the ESP32-S3",
            corner_radius=8
        )
        self.change_credentials_remotely_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Client ID entry change
        self.client_id_entry_change = LabeledEntry(
            master=self.change_credentials_remotely_tab,
            label_text="Client ID",
            placeholder_text="Enter Client ID",
        )
        self.client_id_entry_change.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew"
        )

        # -- Client Secret entry change
        self.client_secret_entry_change = LabeledEntry(
            master=self.change_credentials_remotely_tab,
            label_text="Client Secret",
            placeholder_text="Enter Client Secret",
        )
        self.client_secret_entry_change.grid(row=2, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Redirect URI entry change
        self.redirect_uri_entry_change = LabeledEntry(
            master=self.change_credentials_remotely_tab,
            label_text="Redirect URI",
            placeholder_text="Enter Redirect URI",
        )
        self.redirect_uri_entry_change.grid(row=3, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Redirect URI entry change
        self.refresh_token_entry_change = LabeledEntry(
            master=self.change_credentials_remotely_tab,
            label_text="Refresh Token",
            placeholder_text="Enter Refresh Token",
        )
        self.refresh_token_entry_change.grid(row=4, column=0, padx=10, pady=(20, 10), sticky="ew")

        # -- Confirm credentials button
        self.confirm_credentials_button = ctk.CTkButton(
            master=self.change_credentials_remotely_tab,
            text="Confirm credentials",
            command=self.ask_esp32_ip
        )
        self.confirm_credentials_button.grid(row=5, column=0, padx=10, pady=10)

    # -- Send credentials to ESP32-S3
    def ask_esp32_ip(self):
        # -- Get all entries
        self.client_id_send = self.client_id_entry_change.get().strip() or None
        self.client_secret_send = self.client_secret_entry_change.get().strip() or None
        self.redirect_uri_send = self.redirect_uri_entry_change.get().strip() or None
        self.refresh_token_send = self.refresh_token_entry_change.get().strip() or None

        if self.client_id_send and self.client_secret_send and self.redirect_uri_send and self.refresh_token_send:
            # -- Eliminate all widgets
            self.change_credentials_remotely_label.destroy()
            self.client_id_entry_change.destroy()
            self.client_secret_entry_change.destroy()
            self.redirect_uri_entry_change.destroy()
            self.refresh_token_entry_change.destroy()
            self.confirm_credentials_button.destroy()

            # -- Label for tab
            self.send_credentials_label = ctk.CTkLabel(
                master=self.change_credentials_remotely_tab,
                text="Enter the ip shown in your ESP32-S3",
                corner_radius=8
            )
            self.send_credentials_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

            # -- ESP32 IP entry
            self.esp32_ip_entry = LabeledEntry(
                master=self.change_credentials_remotely_tab,
                label_text="IP",
                placeholder_text="Enter the IP from your ESP32-S3",
            )
            self.esp32_ip_entry.grid(row=1, column=0, padx=10, pady=(20, 10), sticky="ew")

            # -- ESP32 port
            self.esp32_port_entry = LabeledEntry(
                master=self.change_credentials_remotely_tab,
                label_text="Port",
                placeholder_text="Enter the port from your ESP32-S3",
            )
            self.esp32_port_entry.grid(row=2, column=0, padx=10, pady=(20, 10), sticky="ew")

            # -- Confirm credentials button
            self.send_credentials_to_esp32_button = ctk.CTkButton(
                master=self.change_credentials_remotely_tab,
                text="Send credentials",
                command=self.send_credentials_to_esp32
            )
            self.send_credentials_to_esp32_button.grid(row=3, column=0, padx=10, pady=10)

        else:
            print("Something is missing...")

    # -- Send credentials
    def send_credentials_to_esp32(self):
        # Get IP address
        self.esp32_ip = self.esp32_ip_entry.get().strip() or None
        self.esp32_port = self.esp32_port_entry.get().strip() or None

        # ESP32 IP address is given
        if self.esp32_ip and self.esp32_port:
            # Destroy widgets
            self.send_credentials_label.destroy()
            self.esp32_ip_entry.destroy()
            self.esp32_port_entry.destroy()
            self.send_credentials_to_esp32_button.destroy()

            # Try to send 
            try:

                # Build dict according to entered fields
                fields = {
                    "client_id": self.client_id_send,
                    "client_secret": self.client_secret_send,
                    "redirect_uri": self.redirect_uri_send,
                    "refresh_token": self.refresh_token_send,
                }
                spotify = {k: v for k, v in fields.items() if v} or None
                send_values_dict = {"spotify": spotify} if spotify is not None else None

                if send_values_dict is not None:
                    # Push to device
                    esp32_push = self.esp32.push_to_device(
                                                device_ip=self.esp32_ip,
                                                port=int(self.esp32_port),
                                                values=send_values_dict
                                            )

                    if esp32_push == True:
                        # All good!
                        message = ctk.CTkLabel(
                            master=self.change_credentials_remotely_tab,
                            text="All good!\nCredentials were sent.",
                            corner_radius=8
                        )
                        message.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")
                    else:
                        # Something went wrong, error
                        error_label = ctk.CTkLabel(
                            master=self.change_credentials_remotely_tab,
                            text=f"Something went wrong :(\nPlease check ip and port\nError: {esp32_push}",
                            corner_radius=8
                        )
                        error_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")

                else:
                    # Something went wrong, error
                    message = ctk.CTkLabel(
                        master=self.change_credentials_remotely_tab,
                        text=f"Everything was empty, nothing was sent...",
                        corner_radius=8
                    )
                    message.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")
            
            except Exception as e:
                # -- Something went wrong, error
                error_label = ctk.CTkLabel(
                    master=self.change_credentials_remotely_tab,
                    text=f"Something went wrong :(\nPlease check credentials\nError: {e}",
                    corner_radius=8
                )
                error_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")
        
        else:
            print("IP address is empty...")

if __name__ == "__main__":
    app = spotify_app()
    app.mainloop()