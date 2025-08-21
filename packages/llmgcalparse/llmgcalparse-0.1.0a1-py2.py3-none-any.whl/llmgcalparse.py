import argparse
import sys

from chatrepl import Conversation, fputs
from get_multiline_input_with_editor import get_multiline_input_with_editor

if sys.version_info < (3,):
    from urllib import quote
else:
    from urllib.parse import quote

    unicode = str


def generate_google_calendar_event_url(
        unicode_title,
        unicode_start_datetime,
        unicode_end_datetime,
        unicode_description_or_none=None,
        unicode_location_or_none=None,
        unicode_iana_timezone_name_or_none=None
):
    unicode_base_url = u'https://calendar.google.com/calendar/render'

    unicode_query_string_fragments = [
        u'action=TEMPLATE',
        u'text=%s' % quote(unicode_title),
        u'dates=%s/%s' % (unicode_start_datetime, unicode_end_datetime)
    ]

    if unicode_description_or_none is not None:
        unicode_query_string_fragments.append(u'details=%s' % quote(unicode_description_or_none))

    if unicode_location_or_none is not None:
        unicode_query_string_fragments.append(u'location=%s' % quote(unicode_location_or_none))

    if unicode_iana_timezone_name_or_none is not None:
        unicode_query_string_fragments.append(u'ctz=%s' % quote(unicode_iana_timezone_name_or_none))

    unicode_query_string = u'&'.join(unicode_query_string_fragments)

    return u'%s?%s' % (unicode_base_url, unicode_query_string)


def get_and_print_model_response(conv, unicode_message):
    response_fragments = []

    fputs(u"'''", sys.stdout)
    for _ in conv.send_message_to_model_and_stream_response(unicode_message):
        response_fragments.append(_)
        fputs(_, sys.stdout)
    fputs(u"'''\n", sys.stdout)

    return u''.join(response_fragments)


if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument('--api-key', type=str, required=False, help='API key')
    parser.add_argument('--base-url', type=str, required=False, help='Base URL')
    parser.add_argument('--model', type=str, required=False, help='Model name')

    # Parse arguments
    args = parser.parse_args()

    if (
        not args.api_key
        or not args.base_url
        or not args.model
    ):
        parser.error('Must provide --api-key, --base-url, and --model')

    conversation = Conversation(args.api_key, args.base_url, args.model)

    unicode_event_natural_language_description = get_multiline_input_with_editor(
        unicode_prompt_at_bottom=u'# Enter natural language description of event above. Lines starting with # will be ignored.'
    )
    conversation.add_message(unicode_event_natural_language_description)

    fputs(u'\nModel-generated event title: ', sys.stdout)
    unicode_model_generated_event_title = get_and_print_model_response(conversation, u'event title: ')
    unicode_corrected_event_title = get_multiline_input_with_editor(
        unicode_initial_input=unicode_model_generated_event_title,
        unicode_prompt_at_bottom=u'# Edit model-generated event title above. Lines starting with # will be ignored.'
    )
    conversation.correct_last_response(unicode_corrected_event_title)

    fputs(u'\nModel-generated start datetime (YYYYMMDDTHHMMSS): ', sys.stdout)
    unicode_model_generated_start_datetime = get_and_print_model_response(conversation, u'start datetime (YYYYMMDDTHHMMSS): ')
    unicode_corrected_start_datetime = get_multiline_input_with_editor(
        unicode_initial_input=unicode_model_generated_start_datetime,
        unicode_prompt_at_bottom=u'# Edit model-generated start datetime (YYYYMMDDTHHMMSS) above. Lines starting with # will be ignored.'
    )
    conversation.correct_last_response(unicode_corrected_start_datetime)

    fputs(u'\nModel-generated end datetime (YYYYMMDDTHHMMSS): ', sys.stdout)
    unicode_model_generated_end_datetime = get_and_print_model_response(conversation, u'end datetime (YYYYMMDDTHHMMSS): ')
    unicode_corrected_end_datetime = get_multiline_input_with_editor(
        unicode_initial_input=unicode_model_generated_end_datetime,
        unicode_prompt_at_bottom=u'# Edit model-generated end datetime (YYYYMMDDTHHMMSS) above. Lines starting with # will be ignored.'
    )
    conversation.correct_last_response(unicode_corrected_end_datetime)

    fputs(u'\nModel-generated event description: ', sys.stdout)
    unicode_model_generated_event_description = get_and_print_model_response(conversation, u'event description: ')
    unicode_corrected_event_description = get_multiline_input_with_editor(
        unicode_initial_input=unicode_model_generated_event_description,
        unicode_prompt_at_bottom=u'# Edit model-generated event description above. Lines starting with # will be ignored.'
    )
    conversation.correct_last_response(unicode_corrected_event_description)

    fputs(u'\nModel-generated event location: ', sys.stdout)
    unicode_model_generated_event_location = get_and_print_model_response(conversation, u'event location: ')
    unicode_corrected_event_location = get_multiline_input_with_editor(
        unicode_initial_input=unicode_model_generated_event_location,
        unicode_prompt_at_bottom=u'# Edit model-generated event location above. Lines starting with # will be ignored.'
    )
    conversation.correct_last_response(unicode_corrected_event_location)

    unicode_google_calendar_event_url = generate_google_calendar_event_url(
        unicode_title=unicode_corrected_event_title,
        unicode_start_datetime=unicode_corrected_start_datetime,
        unicode_end_datetime=unicode_corrected_end_datetime,
        unicode_description_or_none=unicode_corrected_event_description,
        unicode_location_or_none=unicode_corrected_event_location
    )

    fputs(u'\nGenerated Google Calendar Event URL: ', sys.stdout)
    fputs(unicode_google_calendar_event_url, sys.stdout)
    fputs(u'\n', sys.stdout)
