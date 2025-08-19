import logging
import subprocess
import sys

from ipywidgets import widgets
from IPython.core.display import display, clear_output


def _handle_kinit_reset_process(username, password, new_password, confirm_password):
    kinit_cmd = ["kinit", username.encode()]

    completed_kinit_reset_process = subprocess.run(
        kinit_cmd,
        input=f"{password}\n{new_password.value}\n{confirm_password.value}\n".encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return completed_kinit_reset_process


def handle_kerberos_reset_password(username, password):
    print(f"\nThe kerberos principal({username}) password must be reset...")

    # Set up the password related widgets
    new_password = widgets.Password(
        value="",
        placeholder="New password",
        description="New password:",
        disabled=False,
        style={"description_width": "initial"},
    )
    confirm_password = widgets.Password(
        value="", placeholder="Confirm", description="Confirm:", disabled=False
    )

    display(new_password, confirm_password)

    reset_button = widgets.Button(
        description="Reset Password",
        disabled=False,
        tooltip="Reset Password",
        button_style="primary",
    )

    output = widgets.Output()
    display(reset_button, output)

    # Do not remove the unused param otherwise the button will become unresponsive
    def _on_button_clicked_reset(b):
        with output:
            clear_output(wait=True)
            # Authenticate with the principal, and check if the inputs are not empty string and match
            if new_password.value and confirm_password.value:
                if new_password.value == confirm_password.value:
                    completed_kinit_reset_process = _handle_kinit_reset_process(
                        username, password, new_password, confirm_password
                    )

                    new_password.layout = {"border": "0px"}
                    confirm_password.layout = {"border": "0px"}

                    if completed_kinit_reset_process.returncode == 0:
                        print(
                            "Successfully changed the password!\nPlease restart the kernel and authenticate again with the new password!"
                        )
                    else:
                        raise RuntimeError(
                            f"Error while resetting the password.\nError Code: {completed_kinit_reset_process.returncode}\nstdout: {completed_kinit_reset_process.stdout}\nstderr: {completed_kinit_reset_process.stderr}"
                        )

                else:
                    new_password.layout = {"border": "1px solid #FF0000"}
                    confirm_password.layout = {"border": "1px solid #FF0000"}
                    print("The passwords you entered above must match!\n")
            else:
                new_password.layout = {"border": "1px solid #FF0000"}
                confirm_password.layout = {"border": "1px solid #FF0000"}
                print("The passwords must not be empty!\n")

    reset_button.on_click(_on_button_clicked_reset)
