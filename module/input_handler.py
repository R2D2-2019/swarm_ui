from module.command_node import Node, Command


class input_handler:
    def __init__(self, cli_controller):
        self.cli_controller = cli_controller

    @staticmethod
    def print_command_not_found(command: str) -> None:
        """
        Prints command not found text with the command parameter.
        """
        print(
            "\tCommand '{}' not found, type 'help' for possible commands.".format(
                command
            )
        )

    @staticmethod
    def check_amount_parameters(parameters: list, required_amount: int):
        """
        compares the length of the parameters list to the required amount,
        returns true when the length of the parameters is equal to the required amount
        prints to user if not enough or too many parameters
        """
        if len(parameters) < required_amount or len(parameters) > required_amount:
            print(
                "\tExpected {} parameters, got {}.".format(
                    required_amount, len(parameters)
                )
            )
            return False
        return True

    def handle_help(self, help_parameters):
        try:
            node = self.cli_controller.current_node

            for param in help_parameters:
                node = node[param.upper()]

            self.cli_controller.print_help(node)
        except IndexError:
            self.cli_controller.print_help(self.cli_controller.current_node)
        except KeyError:
            self.print_command_not_found(param)

    def handle_select(self, select_parameters) -> bool:
        if not self.check_amount_parameters(select_parameters, 1):
            return False
        if not select_parameters[0] in self.cli_controller.possible_targets:
            print("\tInvalid parameter '{}'".format(select_parameters[0]))
            return False

        self.cli_controller.set_target(select_parameters[0])
        print("\tYou selected {}".format(select_parameters[0]))
        return True

    @staticmethod
    def convert_type(convertable, convert_type):
        if convert_type is bool:
            if convertable.upper() == "TRUE":
                convertable = True
            elif convertable.upper() == "FALSE":
                convertable = False
            else:
                convertable = bool(int(convertable))

        elif convert_type is int:
            convertable = int(convertable)

        return convertable

    def _handle_category_command(self, command, params) -> None:
        """
        Handles all non-global commands. Returns false if failed or
        if a function has been executed(in this case no other commands can be executed after).
        Returns true if another command can be executed after this one
        """
        category = self.cli_controller.target[1]

        if command not in category:
            self.print_command_not_found(command)
            return

        required_params = category[command]

        if not self.check_amount_parameters(params, len(required_params)):
            return

        # Validate if the user paramters are of the correct type.
        # Print invalid type if type is invalid, this code evaluates all parameters.
        correct_params = True
        for i, param in enumerate(required_params):
            try:
                params[i] = self.convert_type(params[i], required_params[param])
            except ValueError:
                print(
                    "\tInvalid type for parameter {} '{}', expected '{}'".format(
                        i, param, required_params[param]
                    )
                )
                correct_params = False

        if not correct_params:
            return

        print("\tSending command:", command, params, self.cli_controller.target[0])
        category[command].send(
            self.cli_controller.comm, params, self.cli_controller.target[0]
        )

    def _handle_command(self, command: str, params: list):
        if command in self.cli_controller.global_commands:
            self.cli_controller.global_commands[command](params)
        elif self.cli_controller.target:
            self._handle_category_command(command, params)
        else:
            print("No target..")

    def handle_input(self, input_words: list) -> None:
        """
        Execute a command depending on text entered
        """
        command = []
        while input_words:
            word = input_words.pop(0)

            if word == "&&":
                self._handle_command(command[0].upper(), command[1:])
                command = []
                continue

            command.append(word)

            if input_words == []:
                self._handle_command(command[0].upper(), command[1:])
