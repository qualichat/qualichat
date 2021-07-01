# class GraphGenerator:
#     """This class provides the ability to generate graphs.
    
#     Attributes
#     ----------
#     chats: List[:class:`.Qualichat`]
#         The list of chats to be analyzed.
#     """

#     __slots__ = ('chats',)
    
#     def __init__(self, chats: Union[Qualichat, List[Qualichat]]):
#         if isinstance(chats, Qualichat):
#             chats = [chats]

#         self.chats = chats

#         term = 'graph' + ('' if len(chats) == 1 else 's')
#         log('info', f'Created a graph generator for {len(chats)} {term}.')

#     @generate_graph(
#         bars=['Qty_char_!', 'Qty_char_?'],
#         lines=['Qty_messages'],
#         title='Amount by Users'
#     )
#     def users_messages_marks(self):
#         """hows the amount of exclamation points and question marks
#         sent by user.
#         """
#         chat = self.chats[0]
#         data = {}

#         columns = ['Qty_char_!', 'Qty_char_?', 'Qty_messages']
#         indexes = [actor.display_name for actor in chat.actors]

#         rows = []

#         for actor in chat.actors:
#             exclamation_marks = 0
#             question_marks = 0
#             messages = 0

#             for message in actor.messages:
#                 exclamation_marks += get_length(message['Qty_char_!'])
#                 question_marks += get_length(message['Qty_char_?'])
#                 messages += 1

#             rows.append([exclamation_marks, question_marks, messages])            
    
#         dataframe = DataFrame(rows, index=indexes, columns=columns)
#         return dataframe[:10].sort_values(columns, ascending=False)

#     @generate_graph(
#         bars=['Qty_char_!', 'Qty_char_?'],
#         lines=['Qty_char_text', 'Qty_messages'],
#         title='Amount by Month'
#     )
#     def message_marks(self):
#         """Shows the amount of exclamation points and question marks
#         sent in the chat.
#         """
#         chat = self.chats[0]
#         data = defaultdict(list)

#         columns = ['Qty_char_!', 'Qty_char_?', 'Qty_char_text', 'Qty_messages']
#         rows = []

#         for message in chat.messages:
#             index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
#             data[index.strftime('%B %Y')].append(message)

#         for values in data.values():
#             exclamation_marks = 0
#             question_marks = 0
#             pure_content = 0
#             messages = 0

#             for message in values:
#                 exclamation_marks += len(''.join(message['Qty_char_!']))
#                 question_marks += len(''.join(message['Qty_char_?']))
#                 pure_content += len(message['Qty_char_text'])
#                 messages += 1

#             rows.append(
#                 [exclamation_marks, question_marks, pure_content, messages]
#             )

#         return DataFrame(rows, index=data.keys(), columns=columns)

#     def news(self):
#         """..."""
#         chat = self.chats[0]
#         data = defaultdict(int)

#         for message in chat.messages:
#             for url in message['Qty_char_links']:
#                 data[url] += 1

#         sorted_dict = {k: v for k, v in sorted(data.items(), key=lambda i: i[1])[:10]}
#         print(sorted_dict)
