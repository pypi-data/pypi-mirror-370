"""
Models used to represent JSON schemas and Snowflake view definitions.
This was originally internal to the Sync Engine, but was moved to the
plugin runtime so that it could be used for testing column expressions (formulas, etc).
"""
from typing import Any, Dict, Optional, Literal, List, Union, Tuple
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator, computed_field
from jinja2 import Environment
from .logging import logger

class JsonSchemaProperty(BaseModel):
    """
    The most basic common properties for a JSON schema property, plus the extra ones we use for providing Snowflake-specific information.
    Used mainly to do partial parsing as we extract fields from within the schema
    """

    type: Optional[Union[str,List[str]]] = Field(..., description="The type of the property")
    ref: Optional[str] = Field(
        None, description="The reference to another schema", alias="$ref"
    )
    nullable: bool = Field(
        True, description="Whether the property is nullable"
    )
    description: Optional[str] = Field(
        None, description="The description of the property"
    )
    format: Optional[str] = Field(
        None, description="The format of the property, e.g. date-time"
    )
    properties: Optional[Dict[str, Self]] = Field(
        None, description="The sub-properties of the property, if the property is an object type"
    )
    snowflakeTimestampType: Optional[Literal['TIMESTAMP_TZ','TIMESTAMP_NTZ','TIMESTAMP_LTZ']] = Field(
        None, description="The Snowflake timestamp type to use when interpreting a date-time string."
    )
    snowflakeTimestampFormat: Optional[str] = Field(
        None, description="The Snowflake timestamp format to use when interpreting a date-time string."
    )
    snowflakePrecision: Optional[int] = Field(
        None, description="The Snowflake precision to assign to the column."
    )
    snowflakeScale: Optional[int] = Field(
        None, description="The Snowflake scale to assign to the column."
    )
    snowflakeColumnExpression: Optional[str] = Field(
        None,description="""When advanced processing is needed, you can provide a value here. Use {{variant_path}} to interpolate the path to the JSON field.""",
    )
    isJoinColumn: Optional[bool] = Field(
        False, description="Whether this column is sourced from a joined stream"
    )
    requiredStreamNames: Optional[List[str]] = Field(
        None, description="The names of the streams that are depended upon by this column, via joins. If these streams are not selected, the column will be omitted."
    )
    referencedFields: Optional[Dict[str,List[str]]] = Field(
        None, description="The names of fields that are referenced by this field, keyed on the stream name (or None if it's the current stream). This is used to order the fields, and also to cascade the removal of unsupported fields (e.g. in formulas)."
    )

    @model_validator(mode='after')
    def validate(self) -> Self:
        # If the type is a list, we need to condense it down to a single string
        if self.type is None:
            if self.ref is None:
                raise ValueError("You must provide either a type or a reference")
        else:
            if isinstance(self.type, list):
                data_types = [t for t in self.type if t != "null"]
                if len(data_types) == 0:
                    raise ValueError(
                        f"For a list of types, you must provide at least one non-null type ({self.type})"
                    )
                self.nullable = "null" in self.type
                self.type = data_types[0]
        return self
    
    @computed_field
    @property
    def precision(self) -> Optional[int]:
        """
        Returns the precision for this property.
        """
        precision = None
        if self.type == "number" or self.type == "integer":
            precision = 38
        if self.snowflakePrecision is not None:
            precision = self.snowflakePrecision
        return precision
    
    @computed_field
    @property
    def scale(self) -> Optional[int]:
        """
        Returns the scale for this property.
        """
        scale = None
        if self.type == "number":
            scale = 19
        if self.type == "integer":
            scale = 0
        if self.snowflakeScale is not None:
            scale = self.snowflakeScale
        return scale
    
    @computed_field
    @property
    def snowflake_data_type(self) -> str:
        """
        Returns the Snowflake data type for this property.
        """
        if self.type is not None:
            if self.type == "string":
                if self.format is not None:
                    if self.format == "date-time":
                        if self.snowflakeTimestampType is not None:
                            return self.snowflakeTimestampType
                        return "TIMESTAMP" # not sure if we should default to something that may vary according to account parameters
                    elif self.format == "time":
                        return "TIME"
                    elif self.format == "date":
                        return "DATE"
                return "VARCHAR"
            elif self.type == "number":
                return "NUMERIC"
            elif self.type == "integer":
                return "NUMERIC"
            elif self.type == "boolean":
                return "BOOLEAN"
            if self.type == "object":
                return "OBJECT"
            if self.type == "array":
                return "ARRAY"
            return "VARCHAR"
        elif self.ref is not None:
            if self.ref == "WellKnownTypes.json#definitions/Boolean":
                return "BOOLEAN"
            elif self.ref == "WellKnownTypes.json#definitions/Date":
                return "DATE"
            elif self.ref == "WellKnownTypes.json#definitions/TimestampWithTimezone":
                return "TIMESTAMP_TZ"
            elif self.ref == "WellKnownTypes.json#definitions/TimestampWithoutTimezone":
                return "TIMESTAMP_NTZ"
            elif self.ref == "WellKnownTypes.json#definitions/TimeWithTimezone":
                return "TIME"
            elif self.ref == "WellKnownTypes.json#definitions/TimeWithoutTimezone":
                return "TIME"
            elif self.ref == "WellKnownTypes.json#definitions/Integer":
                return "NUMERIC"
            elif self.ref == "WellKnownTypes.json#definitions/Number":
                return "NUMERIC"
            return "VARCHAR"


class SnowflakeViewColumn(BaseModel):
    """
    Represents everything needed to express a column in a Snowflake normalized view.
    The name is the column name, the expression is the SQL expression to use in the view.
    In other words, the column definition is "expression as name".
    """
    name: str
    original_name: str = Field(
        ..., description="The name of the column before the column naming transformation is applied"
    )
    expression: str
    comment: Optional[str] = Field(default=None)
    is_join_column: Optional[bool] = Field(
        default=False, description="Whether this column is sourced from a joined stream"
    )
    required_stream_names: Optional[List[str]] = Field(
        default=None, description="The names of the streams that are depended upon by this column, via joins. If these streams are not selected, the column will be omitted"
    )
    referenced_columns: Optional[Dict[str,List[str]]] = Field(
        default=None, description="The names of columns that are referenced by this column, keyed on the stream name (or None if it's the current stream). This is used to order the columns, and also to cascade the removal of unsupported columns (e.g. in formulas)."
    )

    def __repr__(self) -> str:
        return """SnowflakeViewColumn(
    name=%r,
    original_name=%r,
    expression=%r,
    comment=%r,
    is_join_column=%r,
    required_stream_names=%r,
    referenced_columns=%r)
""" % (
            self.name,
            self.original_name,
            self.expression,
            self.comment,
            self.is_join_column,
            self.required_stream_names,
            self.referenced_columns
        )

    def definition(self,original_name:bool = False, remove_stream_prefix:Optional[str] = None) -> str:
        """
        Returns the column definition for a normalized view.
        If original_name is True, the original name will be used instead of the transformed name.
        """
        if remove_stream_prefix is not None and self.referenced_columns is not None:
            if remove_stream_prefix in self.referenced_columns:
                for referenced_column in self.referenced_columns[remove_stream_prefix]:
                    replace_source = f'"{remove_stream_prefix}"."{referenced_column}"'
                    replace_target = f'"{referenced_column}"'
                    self.expression = self.expression.replace(replace_source, replace_target)
        if original_name:
            return f'{self.expression} as "{self.original_name}"'
        return f'{self.expression} as "{self.name}"'
    
    def original_to_transformed(self) -> str:
        return f'"{self.original_name}" as "{self.name}"'

    def name_with_comment(self,binding_list:Optional[List[Any]] = None) -> str:
        """
        Returns the column name (quoted), along with any comment.
        The resulting text can be used in a CREATE VIEW statement.
        If binding_list is provided, the comment will be added to the list, and a placeholder '?' will be used in the SQL.
        """
        if self.comment is None:
            return f'"{self.name}"'
        if binding_list is not None:
            binding_list.append(self.comment)
            return f'"{self.name}" COMMENT ?'
        return f'"{self.name}" COMMENT $${self.comment}$$'
    
    @classmethod
    def from_json_schema_property(cls,
                                column_name:str,
                                comment:str,
                                variant_path:str,
                                json_schema_property:JsonSchemaProperty,
                                column_name_environment:Environment,
                                column_name_expression:str,
                                plugin_app_database: Optional[str] = None,) -> Self:
        """
        Takes a JSON schema property (which may be nested via variant_path), along with its final name and comment,
        and returns a SnowflakeViewColumn object which is ready to use in a select statement.
        It does this by applying overarching type conversion rules, and evaluating the final column name using Jinja.
        """
        jinja_vars = {"column_name": column_name,"plugin_app_database": plugin_app_database}
        final_column_name = column_name_environment.from_string(column_name_expression).render(**jinja_vars)
        expression = f"""RECORD_DATA:{variant_path}"""
        if json_schema_property.snowflakeColumnExpression:
            jinja_vars = {"variant_path": expression,"plugin_app_database": plugin_app_database}
            expression = column_name_environment.from_string(json_schema_property.snowflakeColumnExpression).render(
                **jinja_vars
            )
        
        if json_schema_property.precision is not None and json_schema_property.scale is not None and json_schema_property.snowflake_data_type == "NUMERIC":
            expression=f"{expression}::NUMERIC({json_schema_property.precision},{json_schema_property.scale})"
        elif json_schema_property.snowflakeTimestampType and json_schema_property.snowflakeTimestampFormat:
            timestamp_type = json_schema_property.snowflakeTimestampType
            timestamp_format = json_schema_property.snowflakeTimestampFormat
            expression=f"""TO_{timestamp_type}({expression}::varchar,'{timestamp_format}')"""
        else:
            if not json_schema_property.snowflakeColumnExpression:
                expression=f"""{expression}::{json_schema_property.snowflake_data_type}"""
        required_stream_names = None
        referenced_columns = None
        if json_schema_property.requiredStreamNames:
            required_stream_names = json_schema_property.requiredStreamNames
        if json_schema_property.referencedFields:
            referenced_columns = json_schema_property.referencedFields
        return cls(
            name=final_column_name,
            original_name=column_name,
            expression=expression,
            comment=comment,
            is_join_column=json_schema_property.isJoinColumn,
            required_stream_names=required_stream_names,
            referenced_columns=referenced_columns
        )
    
    @classmethod
    def order_by_reference(cls,current_stream_name:str,columns:List[Self]) -> List[Self]:
        """
        In some situations, column expressions may reference the alias of another column
        This is allowed in Snowflake, as long as the aliased column is defined before it's used in a later column
        So we need to sort the columns so that if the name of the column appears (in quotes) in the expression of another column, it is ordered first
        """
        logger.debug(
            f"Ordering columns by reference for stream: {current_stream_name} ({len(columns)} columns)"
        )
        # Collect columns to be moved
        columns_to_move:List[Self] = []
        # Collect Omnata System columns and keep them at the front
        omnata_system_columns_start = []
        for column in columns[:]:
            if column.original_name.startswith("OMNATA_"):
                columns.remove(column)
                omnata_system_columns_start.append(column)

        for column in columns:
            for other_column in columns:
                if column==other_column:
                    continue
                if column.original_name in (other_column.referenced_columns or {}).get(current_stream_name,[]):
                    if column not in columns_to_move:
                        logger.debug(
                            f"Column {column.original_name} references {other_column.original_name}, moving it to the front"
                        )
                        columns_to_move.append(column)
        # we need to do another pass just on columns_to_move, because they may reference each other
        # if any do, they go to the front, otherwise they are appended
        columns_to_move_final:List[Self] = []
        for column in columns_to_move:
            for other_column in columns_to_move:
                if column==other_column:
                    continue
                if column.original_name in (other_column.referenced_columns or {}).get(current_stream_name,[]):
                    if column not in columns_to_move_final:
                        logger.debug(
                            f"Second pass: Column {column.original_name} is referenced by {other_column.original_name}, moving it to the front"
                        )
                        columns_to_move_final.insert(0, column)
                        continue
            if column not in columns_to_move_final:
                columns_to_move_final.append(column)
        
        # Move collected columns to the front
        columns_to_move_final.reverse()
        for column in columns_to_move_final:
            columns.remove(column)
            columns.insert(0, column)
        return omnata_system_columns_start + columns


class SnowflakeViewJoin(BaseModel):
    """
    Represents a join in a Snowflake normalized view.
    """

    left_alias: str = Field(
        ..., description="The alias to use on the left side of the join"
    )
    left_column: str = Field(
        ..., description="The column to join on from the left side"
    )
    join_stream_name: str = Field(
        ..., description="The name of the stream to join (right side)"
    )
    join_stream_alias: str = Field(
        ...,
        description="The alias to use for the joined stream, this is used in the column definitions instead of the stream name, and accomodates the possibility of multiple joins to the same stream",
    )
    join_stream_column: str = Field(
        ..., description="The column to join on from the right side"
    )

    def __repr__(self) -> str:
        return (
            "SnowflakeViewJoin(left_alias=%r, left_column=%r, join_stream_name=%r, join_stream_alias=%r, join_stream_column=%r)"
            % (
                self.left_alias,
                self.left_column,
                self.join_stream_name,
                self.join_stream_alias,
                self.join_stream_column,
            )
        )

    def definition(self) -> str:
        """
        Returns the SQL for a single join in a normalized view
        """
        # we don't need to fully qualify the table name, because they'll be aliased in CTEs
        return f"""LEFT JOIN "{self.join_stream_name}" as "{self.join_stream_alias}" 
ON "{self.left_alias}"."{self.left_column}" = "{self.join_stream_alias}"."{self.join_stream_column}" """


class FullyQualifiedTable(BaseModel):
    """
    Represents a fully qualified table name in Snowflake, including database, schema, and table name.
    This is not a template, it's a fully specified object.
    """

    database_name: Optional[str] = Field(default=None, description="The database name")
    schema_name: str = Field(..., description="The schema name")
    table_name: str = Field(..., description="The table name")

    def get_fully_qualified_name(self, table_override: Optional[str] = None) -> str:
        """
        If table_override is provided, it will be used instead of the table name
        """
        actual_table_name = (
            self.table_name if table_override is None else table_override
        )
        # We try to make this resilient to quoting
        schema_name = self.schema_name.replace('"', "")
        table_name = actual_table_name.replace('"', "")
        if self.database_name is None or self.database_name == "":
            return f'"{schema_name}"."{table_name}"'
        database_name = self.database_name.replace('"', "")
        return f'"{database_name}"."{schema_name}"."{table_name}"'

    def get_fully_qualified_stage_name(self) -> str:
        """
        Stage name is derived from the table name
        """
        return self.get_fully_qualified_name(table_override=f"{self.table_name}_STAGE")

    def get_fully_qualified_criteria_deletes_table_name(self) -> str:
        """
        Deletes table name is derived from the table name
        """
        return self.get_fully_qualified_name(
            table_override=f"{self.table_name}_CRITERIA_DELETES"
        )
    
    def get_fully_qualified_state_register_table_name(self) -> str:
        """
        Returns the fully qualified name of the state register table.
        This is used to store state values for syncs, paired with query IDs to use with time travel.
        """
        return self.get_fully_qualified_name(table_override=f"{self.table_name}_STATE_REGISTER")

    def get_fully_qualified_state_register_table_sequence_name(self) -> str:
        """
        Returns the fully qualified name of the state register table.
        This is used to store state values for syncs, paired with query IDs to use with time travel.
        """
        return self.get_fully_qualified_name(table_override=f"{self.table_name}_STATE_REGISTER_SEQ")

class SnowflakeViewPart(BaseModel):
    """
    Represents a stream within a normalized view.
    Because a normalized view can be built from multiple streams, this is potentially only part of the view.
    """
    stream_name: str = Field(..., description="The name of the stream")
    raw_table_location: FullyQualifiedTable = Field(
        ..., description="The location of the raw table that the stream is sourced from"
    )
    comment: Optional[str] = Field(
        None, description="The comment to assign to the view"
    )
    columns: List[SnowflakeViewColumn] = Field(
        ..., description="The columns to include in the view"
    )
    joins: List[SnowflakeViewJoin] = Field(
        ..., description="The joins to include in the view"
    )

    def direct_columns(self) -> List[SnowflakeViewColumn]:
        """
        Returns the columns that are not sourced from joins.
        """
        return [c for c in self.columns if not c.is_join_column]

    def join_columns(self) -> List[SnowflakeViewColumn]:
        """
        Returns the columns that are sourced from joins.
        """
        return [c for c in self.columns if c.is_join_column]

    def comment_clause(self) -> str:
        """
        Returns the comment clause for the view definition.
        """
        return f"COMMENT = $${self.comment}$$ " if self.comment is not None else ""

    def column_names_with_comments(self,binding_list:Optional[List[Any]] = None) -> List[str]:
        """
        Returns a list of column names with comments, suitable for use in a CREATE VIEW statement.
        This includes direct columns first, followed by join columns.
        If binding_list is provided, the comments will be added to the list, and a placeholder '?' will be used in the SQL.
        Otherwise, the comments will be included in the SQL inside of a '$$' delimiter.
        """
        # the outer view definition has all of the column names and comments, but with the direct columns
        # first and the join columns last, same as they are ordered in the inner query
        return [
            c.name_with_comment(binding_list) for c in self.columns
        ]
    
    def cte_text(self,original_name: bool = False, include_only_columns:Optional[List[str]] = None) -> str:
        """
        Returns the CTE text for this view part.
        """
        if include_only_columns is None:
            return f""" "{self.stream_name}" as (
    select {', '.join([c.definition(original_name=original_name,remove_stream_prefix=self.stream_name) for c in self.direct_columns()])} 
    from {self.raw_table_location.get_fully_qualified_name()}
) """
        return f""" "{self.stream_name}" as (
    select {', '.join([c.definition(original_name=original_name,remove_stream_prefix=self.stream_name) for c in self.columns
                       if c.original_name in include_only_columns])} 
    from {self.raw_table_location.get_fully_qualified_name()}
) """
    
    def columns_missing(self,columns_to_check:List[str]) -> List[str]:
        """
        Returns a list of columns that are missing from the view part.
        """
        return [c for c in columns_to_check if c not in [c.original_name for c in self.columns]]

class SnowflakeViewParts(BaseModel):
    """
    Represents a set of streams within a normalized view.
    This is the top level object that represents the whole view.
    """

    main_part: SnowflakeViewPart = Field(
        ..., description="The main part of the view, which is the stream that the view is named after"
    )
    joined_parts: List[SnowflakeViewPart] = Field(
        ..., description="The other streams that are joined to the main stream"
    )

    def view_body(self):
        """
        Creates a view definition from the parts.
        The view will consist of CTEs for all of the involved streams, and these will use their original column names without transformation.
        There will be a final SELECT statement that selects all columns from the main stream, and then adds any columns obtained via joins.
        In the final select statement, the join columns will be aliased with their transformed names.
        """
        # Deduplicate the joined parts
        joined_parts_deduped:List[SnowflakeViewPart] = []
        for part in self.joined_parts:
            if part.stream_name!=self.main_part.stream_name and part.stream_name not in [p.stream_name for p in joined_parts_deduped]:
                joined_parts_deduped.append(part)

        # first, we need to collapse all referenced columns into a single map
        all_referenced_columns:Dict[str,List[str]] = {}
        for part in [self.main_part] + self.joined_parts:
            # if the main part references any columns in this part in its joins, we need to include those columns
            aliases_for_stream = [j.join_stream_alias for j in self.main_part.joins 
                if j.join_stream_name == part.stream_name]
            columns_used_in_joins = [
                j.left_column for j in self.main_part.joins if j.left_alias in aliases_for_stream
            ]
            if part.stream_name not in all_referenced_columns:
                all_referenced_columns[part.stream_name] = []
            all_referenced_columns[part.stream_name] += columns_used_in_joins
            for column in part.columns:
                if column.referenced_columns:
                    for stream_name, referenced_columns in column.referenced_columns.items():
                        if stream_name not in all_referenced_columns:
                            all_referenced_columns[stream_name] = []
                        all_referenced_columns[stream_name] += referenced_columns
            for join in part.joins:
                if join.join_stream_name not in all_referenced_columns:
                    all_referenced_columns[join.join_stream_name] = []
                all_referenced_columns[join.join_stream_name].append(join.join_stream_column)
                all_referenced_columns[part.stream_name].append(join.left_column)


        ctes = [
                self.main_part.cte_text(original_name=True)
            ] + [
                part.cte_text(original_name=True,include_only_columns=all_referenced_columns.get(part.stream_name)) 
            for part in joined_parts_deduped
        ]
        # we need a final CTE which selects the main part's direct columns and joined columns, with their original names
        # then the final select statement will just be aliasing to the transformed names
        final_cte = f""" OMNATA_FINAL_CTE as (
            select {', '.join(
            [
                f'"{self.main_part.stream_name}"."{c.original_name}"' for c in self.main_part.direct_columns()
            ]+[
                c.definition(original_name=True) for c in self.main_part.join_columns()
            ])}
            from "{self.main_part.stream_name}" """
        if len(self.main_part.joins) > 0:
            join_clauses = [join.definition() for join in self.main_part.joins]
            final_cte += "\n" + ("\n".join(join_clauses))
        final_cte += ")"

        ctes.append(final_cte)
        all_ctes = "\n,".join(ctes)
        main_columns:List[SnowflakeViewColumn] = self.main_part.columns
        column_clauses = [f"\"OMNATA_FINAL_CTE\"."+c.original_to_transformed()
                          for c in main_columns]
        
        view_body = f"""with {all_ctes}
    select {', '.join(column_clauses)}
    from OMNATA_FINAL_CTE """
        
        return view_body

    @classmethod
    def generate(cls,
        raw_stream_locations: Dict[str,FullyQualifiedTable],
        stream_schemas: Dict[str,Dict],
        stream_name: str,
        include_default_columns: bool = True,
        column_name_environment: Environment = Environment(),
        column_name_expression: str = "{{column_name}}",
        plugin_app_database: Optional[str] = None,
    ) -> Self:
        """
        Returns the building blocks required to create a normalized view from a stream.
        This includes any joins that are required, via CTEs.
        """
        logger.debug(f"Generating view parts for stream: {stream_name}")
        # we start with the view parts for the view we are building
        main_stream_view_part = normalized_view_part(
            stream_name=stream_name,
            raw_table_location=raw_stream_locations[stream_name],
            include_default_columns=include_default_columns,
            stream_schema=stream_schemas.get(stream_name),
            column_name_environment=column_name_environment,
            column_name_expression=column_name_expression,
            plugin_app_database=plugin_app_database
        )
        joined_parts:List[SnowflakeViewPart] = []
        # remove the joins from the main part if they are not in the raw stream locations
        main_stream_view_part.joins = [join for join in main_stream_view_part.joins 
                                       if join.join_stream_name in raw_stream_locations
                                       and join.join_stream_name in stream_schemas]

        for join in main_stream_view_part.joins:
            logger.debug(f"Generating view parts for join stream: {join.join_stream_name}")
            joined_parts.append(normalized_view_part(
                stream_name=join.join_stream_name,
                raw_table_location=raw_stream_locations[join.join_stream_name],
                include_default_columns=include_default_columns,
                stream_schema=stream_schemas[join.join_stream_name],
                column_name_environment=column_name_environment,
                column_name_expression=column_name_expression,
                plugin_app_database=plugin_app_database
            ))
        # For each column, the plugin can advise which fields (of the same stream or joined) are required for the join, which comes through as referenced_columns
        # on the SnowflakeViewColumn object.
        # Until this generate function is called with the raw stream names, we don't know which streams the user has actually selected, nor which
        # fields are actually available (some may be dropped due to something like an unsupported formula).
        # First, explicitly check for circular references between tables, erroring if they are found.
        # This must be done before any pruning happens.
        # We need to check both by stream name and by join stream alias
        
        # Build mappings for stream names and aliases
        stream_to_aliases:Dict[str,set] = {}  # stream_name -> set of aliases
        alias_to_stream:Dict[str,str] = {}    # alias -> stream_name
        
        # Initialize with the main stream
        stream_to_aliases[main_stream_view_part.stream_name] = {main_stream_view_part.stream_name}
        alias_to_stream[main_stream_view_part.stream_name] = main_stream_view_part.stream_name
        
        # Process all joins to build the mappings
        for part in [main_stream_view_part] + joined_parts:
            logger.debug(f"Processing joins for stream: {part.stream_name}")
            # Make sure the part's stream name is in the mappings
            if part.stream_name not in stream_to_aliases:
                stream_to_aliases[part.stream_name] = [part.stream_name]
            alias_to_stream[part.stream_name] = part.stream_name
            
            for join in part.joins:
                # Add the join stream alias to the set of aliases for that stream
                if join.join_stream_name not in stream_to_aliases:
                    stream_to_aliases[join.join_stream_name] = set()
                stream_to_aliases[join.join_stream_name].add(join.join_stream_alias)
                
                # Map the alias back to its stream
                alias_to_stream[join.join_stream_alias] = join.join_stream_name
                
                # Also add the left alias mapping
                if join.left_alias not in alias_to_stream:
                    # Try to find which stream this alias belongs to
                    for other_part in [main_stream_view_part] + joined_parts:
                        if other_part.stream_name == join.left_alias:
                            if other_part.stream_name not in stream_to_aliases:
                                stream_to_aliases[other_part.stream_name] = set()
                            stream_to_aliases[other_part.stream_name].add(join.left_alias)
                            alias_to_stream[join.left_alias] = other_part.stream_name
                            break
        
        # Build a graph of references between streams and their aliases
        circular_refs:Dict[Tuple[str,str],List[Tuple[str,List[str]]]] = {}  # (source, target) -> [(column_name, ref_fields)]
        
        # First, add references based on column dependencies
        for part in [main_stream_view_part] + joined_parts:
            for column in part.columns:
                if column.referenced_columns:
                    for ref_stream_name, ref_fields in column.referenced_columns.items():
                        # Record this reference by stream name
                        key = (part.stream_name, ref_stream_name)
                        if key not in circular_refs:
                            circular_refs[key] = []
                        circular_refs[key].append((column.original_name, ref_fields))
                        
                        # Also record references by aliases
                        # For each alias of the source stream
                        for source_alias in stream_to_aliases.get(part.stream_name, {part.stream_name}):
                            # For each alias of the target stream
                            for target_alias in stream_to_aliases.get(ref_stream_name, {ref_stream_name}):
                                # Create a reference from source alias to target alias
                                alias_key = (source_alias, target_alias)
                                if alias_key not in circular_refs:
                                    circular_refs[alias_key] = []
                                circular_refs[alias_key].append((column.original_name, ref_fields))
        # Also add references from the joins
        for part in [main_stream_view_part] + joined_parts:
            for join in part.joins:
                # Add a reference from the join stream to the left stream
                key = (join.join_stream_name, part.stream_name)
                if key not in circular_refs:
                    circular_refs[key] = []
                circular_refs[key].append(("join", [join.join_stream_column]))
                
                # Also add references by aliases
                alias_key = (join.join_stream_alias, join.left_alias)
                if alias_key not in circular_refs:
                    circular_refs[alias_key] = []
                circular_refs[alias_key].append(("join", [join.join_stream_column]))
                
                # Add references from the left alias to the join stream alias
                reverse_key = (join.left_alias, join.join_stream_alias)
                if reverse_key not in circular_refs:
                    circular_refs[reverse_key] = []
                circular_refs[reverse_key].append(("join_reverse", [join.left_column]))
        
        # Check for circular references by stream name and by aliases
        for (source, target), refs1 in circular_refs.items():
            source_stream = alias_to_stream.get(source, source)
            target_stream = alias_to_stream.get(target, target)
            
            # Skip references that are just join relationships
            # These are not considered circular references
            if all(ref_type == "join" or ref_type == "join_reverse" for ref_type, _ in refs1):
                continue
            
            # Skip self-references (same stream referencing itself)
            # These are not considered circular references
            if source_stream == target_stream:
                continue
                
            # Check for direct circular references
            reverse_key = (target, source)
            if reverse_key in circular_refs:
                refs2 = circular_refs[reverse_key]
                
                # Skip if both references are just join relationships
                if all(ref_type == "join" or ref_type == "join_reverse" for ref_type, _ in refs2):
                    continue
                
                # Skip if the references are through different aliases
                # This is not a circular reference
                if source != target and target != source:
                    continue
                
                raise ValueError(f"""Cyclic dependency detected: Circular reference between {source} and {target}.
{source} -> {target}: {refs1}
{target} -> {source}: {refs2}""")
            
            # We don't need to check for circular references through aliases
            # because we're already handling them in the direct circular reference check above
                    
        # If we get here, no circular references were found
        logger.debug("No circular references found")
        
        # Now proceed with the actual pruning process
        # First, removing unavailable columns from other streams
        # then, we can do a final pass and remove columns that reference fields that are not available in the current stream
        
        # Now proceed with the actual pruning process
        # First, removing unavailable columns from other streams
        # then, we can do a final pass and remove columns that reference fields that are not available in the current stream

        prune_count = 0
        while prune(main_stream_view_part, joined_parts):
            prune_count += 1
            if prune_count > 10:
                raise ValueError("Pruning of columns from the view has entered an infinite loop")

        return cls(main_part=main_stream_view_part, joined_parts=joined_parts)

def prune(view_part: SnowflakeViewPart, joined_parts: List[SnowflakeViewPart]) -> bool:
    """
    Prunes columns from view parts that reference fields that don't exist in the referenced streams.
    
    This function handles:
    1. Direct dependencies - removing columns that directly reference non-existent columns
    2. Transitive dependencies - removing columns that depend on columns that were removed
    
    Returns True if any columns were removed, False otherwise.
    Raises ValueError if a cyclic dependency is detected.
    """
    columns_removed = False
    
    # Helper function to find a view part by stream name
    def find_part(stream_name: str) -> Optional[SnowflakeViewPart]:
        if stream_name == view_part.stream_name:
            return view_part
        return next((p for p in joined_parts if p.stream_name == stream_name), None)

    # Helper function to check if a column should be kept or removed
    def should_keep_column(column: SnowflakeViewColumn, part: SnowflakeViewPart) -> bool:
        """
        Checks if a column should be kept based on its dependencies.
        Returns True if the column should be kept, False if it should be removed.
        """
        # If no references, keep the column
        if not column.referenced_columns:
            return True
            
        # Check each referenced stream and its fields
        for ref_stream_name, ref_fields in column.referenced_columns.items():
            # Find the referenced part
            ref_part = find_part(ref_stream_name)
            
            # If referenced stream doesn't exist, remove the column
            if ref_part is None:
                logger.warning(
                    f"Column {column.name} in stream {part.stream_name} references stream "
                    f"{ref_stream_name}, but it was not provided"
                )
                return False
                
            # Check each referenced field
            for ref_field in ref_fields:
                # Find the referenced column
                ref_column = next((c for c in ref_part.columns if c.original_name == ref_field), None)
                
                # If referenced column doesn't exist, remove the column
                if ref_column is None:
                    logger.warning(
                        f"Column {column.name} in stream {part.stream_name} references field "
                        f"{ref_field} in stream {ref_stream_name}, but it was not provided"
                    )
                    return False
                    
        # All dependencies are satisfied
        return True
    
    # Process columns for removal
    for column in view_part.columns[:]:  # Use a copy to allow safe removal
        if not should_keep_column(column, view_part):
            view_part.columns.remove(column)
            columns_removed = True
    
    # Process joined parts
    for joined_part in joined_parts:
        # We have to avoid pruning columns that are referenced by joins to this stream.
        # first, we determine all aliases for this stream (multiple join paths back to the same stream are allowed)
        aliases_for_stream = [j.join_stream_alias for j in view_part.joins if j.join_stream_name == joined_part.stream_name]
        # now find all joins using this stream as the join stream
        columns_used_in_joins = [
            j.left_column for j in view_part.joins if j.left_alias in aliases_for_stream
        ]
        for column in joined_part.columns[:]:  # Use a copy to allow safe removal
            # First check if the column is a join column
            if column.original_name in columns_used_in_joins:
                # If it's a join column, we need to keep it
                continue

            if not should_keep_column(column, joined_part):
                joined_part.columns.remove(column)
                columns_removed = True
    
    return columns_removed

class JsonSchemaTopLevel(BaseModel):
    """
    This model is used as a starting point for parsing a JSON schema.
    It does not validate the whole thing up-front, as there is some complex recursion as well as external configuration.
    Instead, it takes the basic properties and then allows for further parsing on demand.
    """
    description: Optional[str] = Field(
        None, description="The description of the schema"
    )
    joins: Optional[List[SnowflakeViewJoin]] = Field(
        None, description="The joins to include in the view"
    )
    properties: Optional[Dict[str, Any]] = Field(
        None, description="The properties of the schema. This is left as a dictionary, and parsed on demand."
    )

    def build_view_columns(self,
            column_name_environment: Environment,                
            column_name_expression: str,
            plugin_app_database: Optional[str] = None,
        ) -> List[SnowflakeViewColumn]:
        """
        Returns a list of column definitions from a json schema
        """
        if self.properties is None:
            return []
        columns = [
            self._extract_view_columns(
                property_name=property_name,
                property_value=property_value,
                column_name_environment=column_name_environment,
                column_name_expression=column_name_expression,
                plugin_app_database=plugin_app_database,
            )
            for property_name, property_value in self.properties.items()
        ]
        return [item for sublist in columns for item in sublist]


    def _extract_view_columns(
        self,
        property_name: str,
        property_value: Dict,
        column_name_environment: Environment,                
        column_name_expression: str,
        current_field_name_path: List[str] = [],
        current_comment_path: List[str] = [],
        plugin_app_database: Optional[str] = None,
    ) -> List[SnowflakeViewColumn]:
        """
        Recursive function which returns a list of column definitions.
        - property_name is the name of the current property.
        - property_value is the value of the current property, (the JSON-schema node).
        - current_field_name_path is [] on initial entry, then contains parent path field names as it recurses.
        - current_comment_path is the same length as above, and contains any "description" values found on the way down
        """
        json_property = JsonSchemaProperty.model_validate(property_value)
        children = []
        if json_property.type:
            if json_property.type == "object":
                # TODO: make this depth configurable on the sync
                if len(current_field_name_path) < 5 and json_property.properties is not None:
                    children = [
                        self._extract_view_columns(
                            property_name=child_property_name,
                            property_value=child_property_value,
                            column_name_environment=column_name_environment,
                            column_name_expression=column_name_expression,
                            current_field_name_path=current_field_name_path + [property_name],
                            current_comment_path=current_comment_path + [json_property.description or ""],
                            plugin_app_database=plugin_app_database,
                        )
                        for child_property_name, child_property_value in json_property.properties.items()
                    ]
                    children = [item for sublist in children for item in sublist]
        current_field_name_path = current_field_name_path + [property_name]
        current_comment_path = current_comment_path + [
            json_property.description or ""
        ]
        # remove empty strings from current_comment_path
        current_comment_path = [c for c in current_comment_path if c]

        columns = [SnowflakeViewColumn.from_json_schema_property(
            column_name="_".join(current_field_name_path),
            comment=" -> ".join(current_comment_path),
            variant_path=":".join([f'"{p}"' for p in current_field_name_path if p]),
            json_schema_property=json_property,
            column_name_environment=column_name_environment,
            column_name_expression=column_name_expression,
            plugin_app_database=plugin_app_database,
        )]
        columns.extend(children)
        return columns
    

def normalized_view_part(
    stream_name:str,
    raw_table_location:FullyQualifiedTable,
    include_default_columns: bool,
    column_name_environment: Environment,                
    column_name_expression: str,
    stream_schema: Optional[Dict] = None,
    plugin_app_database: Optional[str] = None,
) -> SnowflakeViewPart:
    """
    Returns an object containing:
    - A top level comment for the view
    - A list of SnowflakeViewColumn objects, representing the columns to create in the view
    - A list of SnowflakeViewJoin objects, representing the joins to create in the view
    """
    logger.debug(
        f"Building normalized view part for stream: {stream_name}"
    )
    snowflake_columns: List[SnowflakeViewColumn] = []
    if include_default_columns:
        snowflake_columns.append(
            SnowflakeViewColumn(
                name="OMNATA_APP_IDENTIFIER",
                original_name="OMNATA_APP_IDENTIFIER",
                expression="APP_IDENTIFIER",
                comment="The value of the unique identifier for the record in the source system",
            )
        )
        snowflake_columns.append(
            SnowflakeViewColumn(
                name="OMNATA_RETRIEVE_DATE",
                original_name="OMNATA_RETRIEVE_DATE",
                expression="RETRIEVE_DATE",
                comment="The date and time the record was retrieved from the source system",
            )
        )
        snowflake_columns.append(
            SnowflakeViewColumn(
                name="OMNATA_RAW_RECORD",
                original_name="OMNATA_RAW_RECORD",
                expression="RECORD_DATA",
                comment="The raw semi-structured record as retrieved from the source system",
            )
        )
        snowflake_columns.append(
            SnowflakeViewColumn(
                name="OMNATA_IS_DELETED",
                original_name="OMNATA_IS_DELETED",
                expression="IS_DELETED",
                comment="A flag to indicate that the record was deleted from the source system",
            )
        )
        snowflake_columns.append(
            SnowflakeViewColumn(
                name="OMNATA_RUN_ID",
                original_name="OMNATA_RUN_ID",
                expression="RUN_ID",
                comment="A flag to indicate which run the record was last processed in",
            )
        )
    view_columns = snowflake_columns
    joins = []
    comment = None
    if stream_schema is not None:
        logger.debug(
            f"Building view columns for stream: {stream_name}"
        )
        json_schema = JsonSchemaTopLevel.model_validate(stream_schema)
        view_columns += json_schema.build_view_columns(
            column_name_environment=column_name_environment,
            column_name_expression=column_name_expression,
            plugin_app_database=plugin_app_database,
        )
        if json_schema.joins:
            joins = json_schema.joins
        comment = json_schema.description
    
    direct_view_columns = [c for c in view_columns if c.is_join_column]
    join_view_columns = [c for c in view_columns if not c.is_join_column]
    # The final order of view columns is:
    #- APP_IDENTIFIER
    #- Direct and joined columns, ordered so that columns that reference other columns are defined after the columns they reference
    #- OMNATA_RETRIEVE_DATE, OMNATA_RAW_RECORD, OMNATA_IS_DELETED, OMNATA_RUN_ID
    view_columns = SnowflakeViewColumn.order_by_reference(stream_name,direct_view_columns +
                                                              join_view_columns)
    return SnowflakeViewPart(
        stream_name=stream_name,
        raw_table_location=raw_table_location,
        columns=view_columns,
        joins=joins,
        comment=comment
    )
