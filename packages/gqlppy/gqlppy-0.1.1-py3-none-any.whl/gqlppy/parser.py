from lark import Lark, Tree, UnexpectedInput
from typing import Callable, IO, Optional, Union

class Parser():
   """A full ISO GQL parser based on a lark grammar derived from the ISO published EBNF.
   """

   def __init__(self, kind: str ='earley', strict: bool=False, starting_productions: list[str] = None):
      """Constructs a ISO GQL parser

      Args:
          kind (str, optional): The algorithm for the lark parser. Defaults to 'earley'.
          strict (bool, optional): Enables strict parsing the lark parser. Defaults to False.
          starting_productions (list[str], optional): The list of productions to allow as starting productions. Defaults to ['gql_program','query_specification','create_graph_type_statement']
      """
      self._starting_productions = ['gql_program','query_specification','create_graph_type_statement'] if starting_productions is None else starting_productions
      self._parser = Lark.open_from_package(
         __name__,
         'gql.lark',
         start=self._starting_productions,
         parser=kind,
         debug=True,
         strict=strict
      )

   def parse(self, text : Union[str,IO], production: str='gql_program', on_error: Optional[Callable[[UnexpectedInput], bool]] = None) -> Tree:
      """Parses a text or stream according to the production specified.

      Args:
          text: The input ISO GQL program or syntax - string or IO
          production (str, optional): A starting production grammar. Defaults to 'gql_program'.

      Returns:
          Tree: A lark post-parse tree
      """
      if not isinstance(text,str):
         text = text.read()
      return self._parser.parse(text, start=production, on_error=on_error)

   def parse_query(self, text : Union[str,IO]) -> Tree:
      """A shorthand for parsing starting with the 'query_specification' grammar production

      Args:
          text: The ISO GQL query to parse - string or IO

      Returns:
          Tree: A lark post-parse tree
      """
      return self.parse(text,production='query_specification')

   @property
   def starting_productions(self) -> list[str]:
      """Returns the configured starting productions."""
      return self._starting_productions.copy()

   @property
   def all_productions(self) -> list[str]:
      """Returns all the grammar productions."""
      return [ rule[0].value for rule in self._parser.grammar.rule_defs]
