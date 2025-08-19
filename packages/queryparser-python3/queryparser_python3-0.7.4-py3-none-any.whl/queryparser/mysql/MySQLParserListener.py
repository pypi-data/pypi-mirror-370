# Generated from src/queryparser/mysql/MySQLParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .MySQLParser import MySQLParser
else:
    from MySQLParser import MySQLParser

# This class defines a complete listener for a parse tree produced by MySQLParser.
class MySQLParserListener(ParseTreeListener):

    # Enter a parse tree produced by MySQLParser#relational_op.
    def enterRelational_op(self, ctx:MySQLParser.Relational_opContext):
        pass

    # Exit a parse tree produced by MySQLParser#relational_op.
    def exitRelational_op(self, ctx:MySQLParser.Relational_opContext):
        pass


    # Enter a parse tree produced by MySQLParser#cast_data_type.
    def enterCast_data_type(self, ctx:MySQLParser.Cast_data_typeContext):
        pass

    # Exit a parse tree produced by MySQLParser#cast_data_type.
    def exitCast_data_type(self, ctx:MySQLParser.Cast_data_typeContext):
        pass


    # Enter a parse tree produced by MySQLParser#search_modifier.
    def enterSearch_modifier(self, ctx:MySQLParser.Search_modifierContext):
        pass

    # Exit a parse tree produced by MySQLParser#search_modifier.
    def exitSearch_modifier(self, ctx:MySQLParser.Search_modifierContext):
        pass


    # Enter a parse tree produced by MySQLParser#interval_unit.
    def enterInterval_unit(self, ctx:MySQLParser.Interval_unitContext):
        pass

    # Exit a parse tree produced by MySQLParser#interval_unit.
    def exitInterval_unit(self, ctx:MySQLParser.Interval_unitContext):
        pass


    # Enter a parse tree produced by MySQLParser#transcoding_name.
    def enterTranscoding_name(self, ctx:MySQLParser.Transcoding_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#transcoding_name.
    def exitTranscoding_name(self, ctx:MySQLParser.Transcoding_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#bit_literal.
    def enterBit_literal(self, ctx:MySQLParser.Bit_literalContext):
        pass

    # Exit a parse tree produced by MySQLParser#bit_literal.
    def exitBit_literal(self, ctx:MySQLParser.Bit_literalContext):
        pass


    # Enter a parse tree produced by MySQLParser#boolean_literal.
    def enterBoolean_literal(self, ctx:MySQLParser.Boolean_literalContext):
        pass

    # Exit a parse tree produced by MySQLParser#boolean_literal.
    def exitBoolean_literal(self, ctx:MySQLParser.Boolean_literalContext):
        pass


    # Enter a parse tree produced by MySQLParser#hex_literal.
    def enterHex_literal(self, ctx:MySQLParser.Hex_literalContext):
        pass

    # Exit a parse tree produced by MySQLParser#hex_literal.
    def exitHex_literal(self, ctx:MySQLParser.Hex_literalContext):
        pass


    # Enter a parse tree produced by MySQLParser#number_literal.
    def enterNumber_literal(self, ctx:MySQLParser.Number_literalContext):
        pass

    # Exit a parse tree produced by MySQLParser#number_literal.
    def exitNumber_literal(self, ctx:MySQLParser.Number_literalContext):
        pass


    # Enter a parse tree produced by MySQLParser#string_literal.
    def enterString_literal(self, ctx:MySQLParser.String_literalContext):
        pass

    # Exit a parse tree produced by MySQLParser#string_literal.
    def exitString_literal(self, ctx:MySQLParser.String_literalContext):
        pass


    # Enter a parse tree produced by MySQLParser#char_functions.
    def enterChar_functions(self, ctx:MySQLParser.Char_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#char_functions.
    def exitChar_functions(self, ctx:MySQLParser.Char_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#group_functions.
    def enterGroup_functions(self, ctx:MySQLParser.Group_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#group_functions.
    def exitGroup_functions(self, ctx:MySQLParser.Group_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#number_functions.
    def enterNumber_functions(self, ctx:MySQLParser.Number_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#number_functions.
    def exitNumber_functions(self, ctx:MySQLParser.Number_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#other_functions.
    def enterOther_functions(self, ctx:MySQLParser.Other_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#other_functions.
    def exitOther_functions(self, ctx:MySQLParser.Other_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#time_functions.
    def enterTime_functions(self, ctx:MySQLParser.Time_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#time_functions.
    def exitTime_functions(self, ctx:MySQLParser.Time_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#mysql_sphere_functions.
    def enterMysql_sphere_functions(self, ctx:MySQLParser.Mysql_sphere_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#mysql_sphere_functions.
    def exitMysql_sphere_functions(self, ctx:MySQLParser.Mysql_sphere_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#mysql_udf_functions.
    def enterMysql_udf_functions(self, ctx:MySQLParser.Mysql_udf_functionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#mysql_udf_functions.
    def exitMysql_udf_functions(self, ctx:MySQLParser.Mysql_udf_functionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#functionList.
    def enterFunctionList(self, ctx:MySQLParser.FunctionListContext):
        pass

    # Exit a parse tree produced by MySQLParser#functionList.
    def exitFunctionList(self, ctx:MySQLParser.FunctionListContext):
        pass


    # Enter a parse tree produced by MySQLParser#literal_value.
    def enterLiteral_value(self, ctx:MySQLParser.Literal_valueContext):
        pass

    # Exit a parse tree produced by MySQLParser#literal_value.
    def exitLiteral_value(self, ctx:MySQLParser.Literal_valueContext):
        pass


    # Enter a parse tree produced by MySQLParser#select_expression.
    def enterSelect_expression(self, ctx:MySQLParser.Select_expressionContext):
        pass

    # Exit a parse tree produced by MySQLParser#select_expression.
    def exitSelect_expression(self, ctx:MySQLParser.Select_expressionContext):
        pass


    # Enter a parse tree produced by MySQLParser#alias.
    def enterAlias(self, ctx:MySQLParser.AliasContext):
        pass

    # Exit a parse tree produced by MySQLParser#alias.
    def exitAlias(self, ctx:MySQLParser.AliasContext):
        pass


    # Enter a parse tree produced by MySQLParser#bit_expr.
    def enterBit_expr(self, ctx:MySQLParser.Bit_exprContext):
        pass

    # Exit a parse tree produced by MySQLParser#bit_expr.
    def exitBit_expr(self, ctx:MySQLParser.Bit_exprContext):
        pass


    # Enter a parse tree produced by MySQLParser#bool_primary.
    def enterBool_primary(self, ctx:MySQLParser.Bool_primaryContext):
        pass

    # Exit a parse tree produced by MySQLParser#bool_primary.
    def exitBool_primary(self, ctx:MySQLParser.Bool_primaryContext):
        pass


    # Enter a parse tree produced by MySQLParser#case_when_statement.
    def enterCase_when_statement(self, ctx:MySQLParser.Case_when_statementContext):
        pass

    # Exit a parse tree produced by MySQLParser#case_when_statement.
    def exitCase_when_statement(self, ctx:MySQLParser.Case_when_statementContext):
        pass


    # Enter a parse tree produced by MySQLParser#case_when_statement1.
    def enterCase_when_statement1(self, ctx:MySQLParser.Case_when_statement1Context):
        pass

    # Exit a parse tree produced by MySQLParser#case_when_statement1.
    def exitCase_when_statement1(self, ctx:MySQLParser.Case_when_statement1Context):
        pass


    # Enter a parse tree produced by MySQLParser#case_when_statement2.
    def enterCase_when_statement2(self, ctx:MySQLParser.Case_when_statement2Context):
        pass

    # Exit a parse tree produced by MySQLParser#case_when_statement2.
    def exitCase_when_statement2(self, ctx:MySQLParser.Case_when_statement2Context):
        pass


    # Enter a parse tree produced by MySQLParser#column_list.
    def enterColumn_list(self, ctx:MySQLParser.Column_listContext):
        pass

    # Exit a parse tree produced by MySQLParser#column_list.
    def exitColumn_list(self, ctx:MySQLParser.Column_listContext):
        pass


    # Enter a parse tree produced by MySQLParser#column_name.
    def enterColumn_name(self, ctx:MySQLParser.Column_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#column_name.
    def exitColumn_name(self, ctx:MySQLParser.Column_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#column_spec.
    def enterColumn_spec(self, ctx:MySQLParser.Column_specContext):
        pass

    # Exit a parse tree produced by MySQLParser#column_spec.
    def exitColumn_spec(self, ctx:MySQLParser.Column_specContext):
        pass


    # Enter a parse tree produced by MySQLParser#displayed_column.
    def enterDisplayed_column(self, ctx:MySQLParser.Displayed_columnContext):
        pass

    # Exit a parse tree produced by MySQLParser#displayed_column.
    def exitDisplayed_column(self, ctx:MySQLParser.Displayed_columnContext):
        pass


    # Enter a parse tree produced by MySQLParser#exp_factor1.
    def enterExp_factor1(self, ctx:MySQLParser.Exp_factor1Context):
        pass

    # Exit a parse tree produced by MySQLParser#exp_factor1.
    def exitExp_factor1(self, ctx:MySQLParser.Exp_factor1Context):
        pass


    # Enter a parse tree produced by MySQLParser#exp_factor2.
    def enterExp_factor2(self, ctx:MySQLParser.Exp_factor2Context):
        pass

    # Exit a parse tree produced by MySQLParser#exp_factor2.
    def exitExp_factor2(self, ctx:MySQLParser.Exp_factor2Context):
        pass


    # Enter a parse tree produced by MySQLParser#exp_factor3.
    def enterExp_factor3(self, ctx:MySQLParser.Exp_factor3Context):
        pass

    # Exit a parse tree produced by MySQLParser#exp_factor3.
    def exitExp_factor3(self, ctx:MySQLParser.Exp_factor3Context):
        pass


    # Enter a parse tree produced by MySQLParser#exp_factor4.
    def enterExp_factor4(self, ctx:MySQLParser.Exp_factor4Context):
        pass

    # Exit a parse tree produced by MySQLParser#exp_factor4.
    def exitExp_factor4(self, ctx:MySQLParser.Exp_factor4Context):
        pass


    # Enter a parse tree produced by MySQLParser#expression.
    def enterExpression(self, ctx:MySQLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by MySQLParser#expression.
    def exitExpression(self, ctx:MySQLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by MySQLParser#expression_list.
    def enterExpression_list(self, ctx:MySQLParser.Expression_listContext):
        pass

    # Exit a parse tree produced by MySQLParser#expression_list.
    def exitExpression_list(self, ctx:MySQLParser.Expression_listContext):
        pass


    # Enter a parse tree produced by MySQLParser#factor1.
    def enterFactor1(self, ctx:MySQLParser.Factor1Context):
        pass

    # Exit a parse tree produced by MySQLParser#factor1.
    def exitFactor1(self, ctx:MySQLParser.Factor1Context):
        pass


    # Enter a parse tree produced by MySQLParser#factor2.
    def enterFactor2(self, ctx:MySQLParser.Factor2Context):
        pass

    # Exit a parse tree produced by MySQLParser#factor2.
    def exitFactor2(self, ctx:MySQLParser.Factor2Context):
        pass


    # Enter a parse tree produced by MySQLParser#factor3.
    def enterFactor3(self, ctx:MySQLParser.Factor3Context):
        pass

    # Exit a parse tree produced by MySQLParser#factor3.
    def exitFactor3(self, ctx:MySQLParser.Factor3Context):
        pass


    # Enter a parse tree produced by MySQLParser#factor4.
    def enterFactor4(self, ctx:MySQLParser.Factor4Context):
        pass

    # Exit a parse tree produced by MySQLParser#factor4.
    def exitFactor4(self, ctx:MySQLParser.Factor4Context):
        pass


    # Enter a parse tree produced by MySQLParser#factor5.
    def enterFactor5(self, ctx:MySQLParser.Factor5Context):
        pass

    # Exit a parse tree produced by MySQLParser#factor5.
    def exitFactor5(self, ctx:MySQLParser.Factor5Context):
        pass


    # Enter a parse tree produced by MySQLParser#function_call.
    def enterFunction_call(self, ctx:MySQLParser.Function_callContext):
        pass

    # Exit a parse tree produced by MySQLParser#function_call.
    def exitFunction_call(self, ctx:MySQLParser.Function_callContext):
        pass


    # Enter a parse tree produced by MySQLParser#groupby_clause.
    def enterGroupby_clause(self, ctx:MySQLParser.Groupby_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#groupby_clause.
    def exitGroupby_clause(self, ctx:MySQLParser.Groupby_clauseContext):
        pass


    # Enter a parse tree produced by MySQLParser#groupby_item.
    def enterGroupby_item(self, ctx:MySQLParser.Groupby_itemContext):
        pass

    # Exit a parse tree produced by MySQLParser#groupby_item.
    def exitGroupby_item(self, ctx:MySQLParser.Groupby_itemContext):
        pass


    # Enter a parse tree produced by MySQLParser#having_clause.
    def enterHaving_clause(self, ctx:MySQLParser.Having_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#having_clause.
    def exitHaving_clause(self, ctx:MySQLParser.Having_clauseContext):
        pass


    # Enter a parse tree produced by MySQLParser#index_hint.
    def enterIndex_hint(self, ctx:MySQLParser.Index_hintContext):
        pass

    # Exit a parse tree produced by MySQLParser#index_hint.
    def exitIndex_hint(self, ctx:MySQLParser.Index_hintContext):
        pass


    # Enter a parse tree produced by MySQLParser#index_hint_list.
    def enterIndex_hint_list(self, ctx:MySQLParser.Index_hint_listContext):
        pass

    # Exit a parse tree produced by MySQLParser#index_hint_list.
    def exitIndex_hint_list(self, ctx:MySQLParser.Index_hint_listContext):
        pass


    # Enter a parse tree produced by MySQLParser#index_name.
    def enterIndex_name(self, ctx:MySQLParser.Index_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#index_name.
    def exitIndex_name(self, ctx:MySQLParser.Index_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#index_list.
    def enterIndex_list(self, ctx:MySQLParser.Index_listContext):
        pass

    # Exit a parse tree produced by MySQLParser#index_list.
    def exitIndex_list(self, ctx:MySQLParser.Index_listContext):
        pass


    # Enter a parse tree produced by MySQLParser#index_options.
    def enterIndex_options(self, ctx:MySQLParser.Index_optionsContext):
        pass

    # Exit a parse tree produced by MySQLParser#index_options.
    def exitIndex_options(self, ctx:MySQLParser.Index_optionsContext):
        pass


    # Enter a parse tree produced by MySQLParser#interval_expr.
    def enterInterval_expr(self, ctx:MySQLParser.Interval_exprContext):
        pass

    # Exit a parse tree produced by MySQLParser#interval_expr.
    def exitInterval_expr(self, ctx:MySQLParser.Interval_exprContext):
        pass


    # Enter a parse tree produced by MySQLParser#join_condition.
    def enterJoin_condition(self, ctx:MySQLParser.Join_conditionContext):
        pass

    # Exit a parse tree produced by MySQLParser#join_condition.
    def exitJoin_condition(self, ctx:MySQLParser.Join_conditionContext):
        pass


    # Enter a parse tree produced by MySQLParser#limit_clause.
    def enterLimit_clause(self, ctx:MySQLParser.Limit_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#limit_clause.
    def exitLimit_clause(self, ctx:MySQLParser.Limit_clauseContext):
        pass


    # Enter a parse tree produced by MySQLParser#match_against_statement.
    def enterMatch_against_statement(self, ctx:MySQLParser.Match_against_statementContext):
        pass

    # Exit a parse tree produced by MySQLParser#match_against_statement.
    def exitMatch_against_statement(self, ctx:MySQLParser.Match_against_statementContext):
        pass


    # Enter a parse tree produced by MySQLParser#offset.
    def enterOffset(self, ctx:MySQLParser.OffsetContext):
        pass

    # Exit a parse tree produced by MySQLParser#offset.
    def exitOffset(self, ctx:MySQLParser.OffsetContext):
        pass


    # Enter a parse tree produced by MySQLParser#row_count.
    def enterRow_count(self, ctx:MySQLParser.Row_countContext):
        pass

    # Exit a parse tree produced by MySQLParser#row_count.
    def exitRow_count(self, ctx:MySQLParser.Row_countContext):
        pass


    # Enter a parse tree produced by MySQLParser#orderby_clause.
    def enterOrderby_clause(self, ctx:MySQLParser.Orderby_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#orderby_clause.
    def exitOrderby_clause(self, ctx:MySQLParser.Orderby_clauseContext):
        pass


    # Enter a parse tree produced by MySQLParser#orderby_item.
    def enterOrderby_item(self, ctx:MySQLParser.Orderby_itemContext):
        pass

    # Exit a parse tree produced by MySQLParser#orderby_item.
    def exitOrderby_item(self, ctx:MySQLParser.Orderby_itemContext):
        pass


    # Enter a parse tree produced by MySQLParser#partition_clause.
    def enterPartition_clause(self, ctx:MySQLParser.Partition_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#partition_clause.
    def exitPartition_clause(self, ctx:MySQLParser.Partition_clauseContext):
        pass


    # Enter a parse tree produced by MySQLParser#partition_name.
    def enterPartition_name(self, ctx:MySQLParser.Partition_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#partition_name.
    def exitPartition_name(self, ctx:MySQLParser.Partition_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#partition_names.
    def enterPartition_names(self, ctx:MySQLParser.Partition_namesContext):
        pass

    # Exit a parse tree produced by MySQLParser#partition_names.
    def exitPartition_names(self, ctx:MySQLParser.Partition_namesContext):
        pass


    # Enter a parse tree produced by MySQLParser#bit_fac1.
    def enterBit_fac1(self, ctx:MySQLParser.Bit_fac1Context):
        pass

    # Exit a parse tree produced by MySQLParser#bit_fac1.
    def exitBit_fac1(self, ctx:MySQLParser.Bit_fac1Context):
        pass


    # Enter a parse tree produced by MySQLParser#bit_fac2.
    def enterBit_fac2(self, ctx:MySQLParser.Bit_fac2Context):
        pass

    # Exit a parse tree produced by MySQLParser#bit_fac2.
    def exitBit_fac2(self, ctx:MySQLParser.Bit_fac2Context):
        pass


    # Enter a parse tree produced by MySQLParser#predicate.
    def enterPredicate(self, ctx:MySQLParser.PredicateContext):
        pass

    # Exit a parse tree produced by MySQLParser#predicate.
    def exitPredicate(self, ctx:MySQLParser.PredicateContext):
        pass


    # Enter a parse tree produced by MySQLParser#query.
    def enterQuery(self, ctx:MySQLParser.QueryContext):
        pass

    # Exit a parse tree produced by MySQLParser#query.
    def exitQuery(self, ctx:MySQLParser.QueryContext):
        pass


    # Enter a parse tree produced by MySQLParser#schema_name.
    def enterSchema_name(self, ctx:MySQLParser.Schema_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#schema_name.
    def exitSchema_name(self, ctx:MySQLParser.Schema_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#select_list.
    def enterSelect_list(self, ctx:MySQLParser.Select_listContext):
        pass

    # Exit a parse tree produced by MySQLParser#select_list.
    def exitSelect_list(self, ctx:MySQLParser.Select_listContext):
        pass


    # Enter a parse tree produced by MySQLParser#select_statement.
    def enterSelect_statement(self, ctx:MySQLParser.Select_statementContext):
        pass

    # Exit a parse tree produced by MySQLParser#select_statement.
    def exitSelect_statement(self, ctx:MySQLParser.Select_statementContext):
        pass


    # Enter a parse tree produced by MySQLParser#simple_expr.
    def enterSimple_expr(self, ctx:MySQLParser.Simple_exprContext):
        pass

    # Exit a parse tree produced by MySQLParser#simple_expr.
    def exitSimple_expr(self, ctx:MySQLParser.Simple_exprContext):
        pass


    # Enter a parse tree produced by MySQLParser#subquery.
    def enterSubquery(self, ctx:MySQLParser.SubqueryContext):
        pass

    # Exit a parse tree produced by MySQLParser#subquery.
    def exitSubquery(self, ctx:MySQLParser.SubqueryContext):
        pass


    # Enter a parse tree produced by MySQLParser#table_atom.
    def enterTable_atom(self, ctx:MySQLParser.Table_atomContext):
        pass

    # Exit a parse tree produced by MySQLParser#table_atom.
    def exitTable_atom(self, ctx:MySQLParser.Table_atomContext):
        pass


    # Enter a parse tree produced by MySQLParser#table_name.
    def enterTable_name(self, ctx:MySQLParser.Table_nameContext):
        pass

    # Exit a parse tree produced by MySQLParser#table_name.
    def exitTable_name(self, ctx:MySQLParser.Table_nameContext):
        pass


    # Enter a parse tree produced by MySQLParser#table_factor1.
    def enterTable_factor1(self, ctx:MySQLParser.Table_factor1Context):
        pass

    # Exit a parse tree produced by MySQLParser#table_factor1.
    def exitTable_factor1(self, ctx:MySQLParser.Table_factor1Context):
        pass


    # Enter a parse tree produced by MySQLParser#table_factor2.
    def enterTable_factor2(self, ctx:MySQLParser.Table_factor2Context):
        pass

    # Exit a parse tree produced by MySQLParser#table_factor2.
    def exitTable_factor2(self, ctx:MySQLParser.Table_factor2Context):
        pass


    # Enter a parse tree produced by MySQLParser#table_factor3.
    def enterTable_factor3(self, ctx:MySQLParser.Table_factor3Context):
        pass

    # Exit a parse tree produced by MySQLParser#table_factor3.
    def exitTable_factor3(self, ctx:MySQLParser.Table_factor3Context):
        pass


    # Enter a parse tree produced by MySQLParser#table_factor4.
    def enterTable_factor4(self, ctx:MySQLParser.Table_factor4Context):
        pass

    # Exit a parse tree produced by MySQLParser#table_factor4.
    def exitTable_factor4(self, ctx:MySQLParser.Table_factor4Context):
        pass


    # Enter a parse tree produced by MySQLParser#table_reference.
    def enterTable_reference(self, ctx:MySQLParser.Table_referenceContext):
        pass

    # Exit a parse tree produced by MySQLParser#table_reference.
    def exitTable_reference(self, ctx:MySQLParser.Table_referenceContext):
        pass


    # Enter a parse tree produced by MySQLParser#table_references.
    def enterTable_references(self, ctx:MySQLParser.Table_referencesContext):
        pass

    # Exit a parse tree produced by MySQLParser#table_references.
    def exitTable_references(self, ctx:MySQLParser.Table_referencesContext):
        pass


    # Enter a parse tree produced by MySQLParser#table_spec.
    def enterTable_spec(self, ctx:MySQLParser.Table_specContext):
        pass

    # Exit a parse tree produced by MySQLParser#table_spec.
    def exitTable_spec(self, ctx:MySQLParser.Table_specContext):
        pass


    # Enter a parse tree produced by MySQLParser#where_clause.
    def enterWhere_clause(self, ctx:MySQLParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by MySQLParser#where_clause.
    def exitWhere_clause(self, ctx:MySQLParser.Where_clauseContext):
        pass



del MySQLParser