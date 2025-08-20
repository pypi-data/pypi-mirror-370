import time

from openobd_protocol.UserInterface.Messages.UserInterface_pb2 import Label, Options, Continue, YesNo, FreeText, \
    Numbers, InterfaceType, Control, LabelTranslations, Image

from openobd.core import StreamHandler, OpenOBDSession

_control_types = Label | Options | Continue | YesNo | FreeText | Numbers
control_mapping = {
    Label: "control_label",
    Options: "control_options",
    Continue: "control_continue",
    YesNo: "control_yesno",
    FreeText: "control_freetext",
    Numbers: "control_number"
}

class UiHandler:

    def __init__(self, openobd_session: OpenOBDSession, target: InterfaceType = InterfaceType.INTERFACE_USER):
        """
        Handles sending user interface (UI) elements to a gRPC stream and parsing their responses.

        :param openobd_session: an active OpenOBDSession with which to start the UI stream.
        :param target: determines who is able to view the user interface.
        """
        self.stream_handler = StreamHandler(openobd_session.open_control_stream, outgoing_stream=True)
        self._target = target

    def show_ui(self, control: _control_types, translations: LabelTranslations | list[LabelTranslations] = None, image: Image = None) -> None | int | bool | str:
        """
        Displays a control object and waits for a response.

        :param control: the control type to be displayed.
        :param translations: Translations for all labels used in this control.
        :param image: Optional image to show next to the control.
        :return: the user's response, depending on which control type has been displayed.
        """
        assert type(control) in control_mapping, f"Received unsupported control type {type(control)}."

        # Allow for providing a single LabelTranslation object for convenience
        if isinstance(translations, LabelTranslations):
            translations = [translations]

        control_arg = {
            control_mapping[type(control)]: control
        }

        self.stream_handler.send(Control(
            target=self._target,
            translations=translations,
            image=image,
            **control_arg
        ), flush_incoming_messages=True)
        while True:
            response = self.stream_handler.receive()

            # Confirm that the received control type matches the control type sent earlier. If not, ignore it
            control_incoming = self._get_control_from_message(response)
            if isinstance(control_incoming, type(control)):
                if hasattr(control_incoming, "answer"):
                    return control_incoming.answer
                else:
                    return None

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream and the UI, if they are not already closed. A new UiHandler object will have to be
        created to open the UI again.
        """
        self.stream_handler.stop_stream()
        time.sleep(1.5)     # Give the UI time to close before continuing

    @staticmethod
    def _get_control_from_message(message: Control) -> _control_types:
        """
        Retrieves the control type from a given Control message.

        :param message: Control message containing a control type.
        :return: the control type present in the given message.
        """
        for control_type in control_mapping.values():
            if message.HasField(control_type):
                return getattr(message, control_type)
