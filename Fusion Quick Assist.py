"""
Fusion Quick Assist - Quick Access Search and Help Add-in for Fusion 360

This add-in for Autodesk Fusion assists users by providing quick access to a searchable database 
and allowing instant queries about Autodesk Fusion features and functionalities through predefined search types like 
ChatGPT, YouTube, and Google. It helps both new and experienced users find answers and tutorials directly within the Autodesk Fusion interface.

Author: brad anderson jr
Email: brad@bradandersonjr.com
GitHub: https://github.com/bradandersonjr
Version: 1.0.0
Date: April 19th, 2024
License: MIT License

Usage:
    - Install the add-in in Autodesk Fusion
    - Access it from the Quick Access Toolbar to initiate searches or queries

Note:
    - Ensure that Autodesk Fusion API is up to date to support all functionalities of this add-in.

"""

import adsk.core, adsk.fusion, traceback, webbrowser

# Handlers list to keep references to the command handlers and prevent garbage collection.
handlers = []

class ButtonCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """
    Handles the creation of a button command, attaching the execution handler to it.
    
    Args:
        ui (adsk.core.UserInterface): The user interface object where the command will be created.
        search_type (str): Type of search ('ChatGPT', 'YouTube', or 'Google') this button pertains to.
    """
    def __init__(self, ui, search_type):
        super().__init__()
        self.ui = ui
        self.search_type = search_type

    def notify(self, args):
        """
        Called when the button command is created. Attaches the execution handler to the command.
        
        Args:
            args: Event arguments that contain the command object.
        """
        try:
            command = args.command
            onExecute = ButtonCommandExecuteHandler(self.ui, self.search_type)
            command.execute.add(onExecute)
            handlers.append(onExecute)  # Store the handler to prevent it from being garbage collected.
        except:
            self.show_error_message(self.ui, traceback.format_exc())

    def show_error_message(self, ui, message):
        """
        Displays an error message in a message box within Fusion 360.

        Args:
            ui (adsk.core.UserInterface): User interface to show the message.
            message (str): Error message to display.
        """
        ui.messageBox(message)

class ButtonCommandExecuteHandler(adsk.core.CommandEventHandler):
    """
    Executes the specific command associated with each button based on the search type.

    Args:
        ui (adsk.core.UserInterface): The user interface object where the command will be executed.
        search_type (str): Type of search ('ChatGPT', 'YouTube', or 'Google') to execute.
    """
    def __init__(self, ui, search_type):
        super().__init__()
        self.ui = ui
        self.search_type = search_type

    def notify(self, args):
        """
        Called when the button is clicked. Handles opening or toggling palettes and performing web searches.
        
        Args:
            args: Event arguments that might be used for further customization (unused here).
        """
        try:
            if self.search_type == "ChatGPT":
                palette_id = 'OpenAIChatGPTPalette'
                palette = self.ui.palettes.itemById(palette_id)
                if not palette:
                    # Create the palette if it doesn't exist.
                    palette = self.ui.palettes.add(palette_id, 'ChatGPT', 'https://chat.openai.com', True, True, True, 530, 500)
                    palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateLeft
                # Toggle the visibility of the palette.
                palette.isVisible = not palette.isVisible
            else:
                # Handle search types for YouTube and Google by prompting for user input.
                if self.search_type == "YouTube":
                    input_title = "Search YouTube for Autodesk Fusion Videos"
                    input_message = "Autodesk Fusion Subject:"
                else:  # Google
                    input_title = "Search Google for Autodesk Fusion Results"
                    input_message = "Autodesk Fusion Subject:"
                
                result = self.ui.inputBox(input_message, input_title, "")
                subject = result[0]  # Get the first element of the input, which is the user's input.

                if subject:
                    # Formulate the URL based on the search type and subject.
                    if self.search_type == "YouTube":
                        search_url = f"https://www.youtube.com/results?search_query=Autodesk+Fusion+360+{subject}"
                    else:
                        search_url = f"https://www.google.com/search?q=Autodesk+Fusion+360+{subject}"
                    # Open the URL in the default web browser.
                    webbrowser.open(search_url)

        except:
            self.show_error_message(self.ui, traceback.format_exc())

    def show_error_message(self, ui, message):
        """
        Displays an error message in a message box within Fusion 360.

        Args:
            ui (adsk.core.UserInterface): User interface to show the message.
            message (str): Error message to display.
        """
        ui.messageBox(message)

def run(context):
    """
    Entry point when the add-in is loaded. Sets up the user interface elements and commands.

    Args:
        context: The context under which the add-in is running, provided by the Fusion 360 environment.
    """
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up any existing command definitions if they exist to avoid duplicates.
        ids_to_check = ['SearchYouTubeID', 'SearchGoogleID', 'ChatGPTID']
        for id in ids_to_check:
            cmdDef = ui.commandDefinitions.itemById(id)
            if cmdDef:
                cmdDef.deleteMe()

        qatRToolbar = ui.toolbars.itemById('QATRight')  # Access the Quick Access Toolbar on the right side.

        # Set up the buttons for YouTube, Google, and ChatGPT searches.
        youtubeButtonDefinition = ui.commandDefinitions.addButtonDefinition('SearchYouTubeID', 'Search YouTube for Autodesk Fusion Videos', '', './resources/YouTube')
        onYoutubeButtonCreated = ButtonCommandCreatedHandler(ui, "YouTube")
        youtubeButtonDefinition.commandCreated.add(onYoutubeButtonCreated)
        handlers.append(onYoutubeButtonCreated)
        qatRToolbar.controls.addCommand(youtubeButtonDefinition, 'HealthStatusCommand', False)

        googleButtonDefinition = ui.commandDefinitions.addButtonDefinition('SearchGoogleID', 'Search Google for Autodesk Fusion Results', '', './resources/Google')
        onGoogleButtonCreated = ButtonCommandCreatedHandler(ui, "Google")
        googleButtonDefinition.commandCreated.add(onGoogleButtonCreated)
        handlers.append(onGoogleButtonCreated)
        qatRToolbar.controls.addCommand(googleButtonDefinition, 'HealthStatusCommand', False)

        chatgptButtonDefinition = ui.commandDefinitions.addButtonDefinition('ChatGPTID', 'ChatGPT Quick Query', '', './resources/ChatGPT')
        onChatGPTButtonCreated = ButtonCommandCreatedHandler(ui, "ChatGPT")
        chatgptButtonDefinition.commandCreated.add(onChatGPTButtonCreated)
        handlers.append(onChatGPTButtonCreated)
        qatRToolbar.controls.addCommand(chatgptButtonDefinition, 'HealthStatusCommand', False)

    except:
        ui.messageBox(traceback.format_exc())

def stop(context):
    """
    Cleanup function when the add-in is unloaded. Removes all UI elements and cleans up resources.

    Args:
        context: The context under which the add-in is being stopped, provided by the Fusion 360 environment.
    """
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        qatRToolbar = ui.toolbars.itemById('QATRight')
        for id in ['SearchYouTubeID', 'SearchGoogleID', 'ChatGPTID']:
            cmd = qatRToolbar.controls.itemById(id)
            if cmd:
                cmd.deleteMe()
    except:
        ui.messageBox(traceback.format_exc())