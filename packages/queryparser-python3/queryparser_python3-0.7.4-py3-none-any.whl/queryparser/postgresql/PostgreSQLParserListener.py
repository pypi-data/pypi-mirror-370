# Generated from src/queryparser/postgresql/PostgreSQLParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .PostgreSQLParser import PostgreSQLParser
else:
    from PostgreSQLParser import PostgreSQLParser

# This class defines a complete listener for a parse tree produced by PostgreSQLParser.
class PostgreSQLParserListener(ParseTreeListener):

    # Enter a parse tree produced by PostgreSQLParser#relational_op.
    def enterRelational_op(self, ctx:PostgreSQLParser.Relational_opContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#relational_op.
    def exitRelational_op(self, ctx:PostgreSQLParser.Relational_opContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#cast_data_type.
    def enterCast_data_type(self, ctx:PostgreSQLParser.Cast_data_typeContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#cast_data_type.
    def exitCast_data_type(self, ctx:PostgreSQLParser.Cast_data_typeContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#bit_literal.
    def enterBit_literal(self, ctx:PostgreSQLParser.Bit_literalContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#bit_literal.
    def exitBit_literal(self, ctx:PostgreSQLParser.Bit_literalContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#boolean_literal.
    def enterBoolean_literal(self, ctx:PostgreSQLParser.Boolean_literalContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#boolean_literal.
    def exitBoolean_literal(self, ctx:PostgreSQLParser.Boolean_literalContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#hex_literal.
    def enterHex_literal(self, ctx:PostgreSQLParser.Hex_literalContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#hex_literal.
    def exitHex_literal(self, ctx:PostgreSQLParser.Hex_literalContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#number_literal.
    def enterNumber_literal(self, ctx:PostgreSQLParser.Number_literalContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#number_literal.
    def exitNumber_literal(self, ctx:PostgreSQLParser.Number_literalContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#string_literal.
    def enterString_literal(self, ctx:PostgreSQLParser.String_literalContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#string_literal.
    def exitString_literal(self, ctx:PostgreSQLParser.String_literalContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#char_functions.
    def enterChar_functions(self, ctx:PostgreSQLParser.Char_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#char_functions.
    def exitChar_functions(self, ctx:PostgreSQLParser.Char_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#group_functions.
    def enterGroup_functions(self, ctx:PostgreSQLParser.Group_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#group_functions.
    def exitGroup_functions(self, ctx:PostgreSQLParser.Group_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#number_functions.
    def enterNumber_functions(self, ctx:PostgreSQLParser.Number_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#number_functions.
    def exitNumber_functions(self, ctx:PostgreSQLParser.Number_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#other_functions.
    def enterOther_functions(self, ctx:PostgreSQLParser.Other_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#other_functions.
    def exitOther_functions(self, ctx:PostgreSQLParser.Other_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#time_functions.
    def enterTime_functions(self, ctx:PostgreSQLParser.Time_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#time_functions.
    def exitTime_functions(self, ctx:PostgreSQLParser.Time_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#array_functions.
    def enterArray_functions(self, ctx:PostgreSQLParser.Array_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#array_functions.
    def exitArray_functions(self, ctx:PostgreSQLParser.Array_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#custom_functions.
    def enterCustom_functions(self, ctx:PostgreSQLParser.Custom_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#custom_functions.
    def exitCustom_functions(self, ctx:PostgreSQLParser.Custom_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#pg_sphere_functions.
    def enterPg_sphere_functions(self, ctx:PostgreSQLParser.Pg_sphere_functionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#pg_sphere_functions.
    def exitPg_sphere_functions(self, ctx:PostgreSQLParser.Pg_sphere_functionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#functionList.
    def enterFunctionList(self, ctx:PostgreSQLParser.FunctionListContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#functionList.
    def exitFunctionList(self, ctx:PostgreSQLParser.FunctionListContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#literal_value.
    def enterLiteral_value(self, ctx:PostgreSQLParser.Literal_valueContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#literal_value.
    def exitLiteral_value(self, ctx:PostgreSQLParser.Literal_valueContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#select_expression.
    def enterSelect_expression(self, ctx:PostgreSQLParser.Select_expressionContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#select_expression.
    def exitSelect_expression(self, ctx:PostgreSQLParser.Select_expressionContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#alias.
    def enterAlias(self, ctx:PostgreSQLParser.AliasContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#alias.
    def exitAlias(self, ctx:PostgreSQLParser.AliasContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#bit_expr.
    def enterBit_expr(self, ctx:PostgreSQLParser.Bit_exprContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#bit_expr.
    def exitBit_expr(self, ctx:PostgreSQLParser.Bit_exprContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#bool_primary.
    def enterBool_primary(self, ctx:PostgreSQLParser.Bool_primaryContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#bool_primary.
    def exitBool_primary(self, ctx:PostgreSQLParser.Bool_primaryContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#case_when_statement.
    def enterCase_when_statement(self, ctx:PostgreSQLParser.Case_when_statementContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#case_when_statement.
    def exitCase_when_statement(self, ctx:PostgreSQLParser.Case_when_statementContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#case_when_statement1.
    def enterCase_when_statement1(self, ctx:PostgreSQLParser.Case_when_statement1Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#case_when_statement1.
    def exitCase_when_statement1(self, ctx:PostgreSQLParser.Case_when_statement1Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#case_when_statement2.
    def enterCase_when_statement2(self, ctx:PostgreSQLParser.Case_when_statement2Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#case_when_statement2.
    def exitCase_when_statement2(self, ctx:PostgreSQLParser.Case_when_statement2Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#column_list.
    def enterColumn_list(self, ctx:PostgreSQLParser.Column_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#column_list.
    def exitColumn_list(self, ctx:PostgreSQLParser.Column_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#column_name.
    def enterColumn_name(self, ctx:PostgreSQLParser.Column_nameContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#column_name.
    def exitColumn_name(self, ctx:PostgreSQLParser.Column_nameContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#column_spec.
    def enterColumn_spec(self, ctx:PostgreSQLParser.Column_specContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#column_spec.
    def exitColumn_spec(self, ctx:PostgreSQLParser.Column_specContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#displayed_column.
    def enterDisplayed_column(self, ctx:PostgreSQLParser.Displayed_columnContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#displayed_column.
    def exitDisplayed_column(self, ctx:PostgreSQLParser.Displayed_columnContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#displayed_column_arr.
    def enterDisplayed_column_arr(self, ctx:PostgreSQLParser.Displayed_column_arrContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#displayed_column_arr.
    def exitDisplayed_column_arr(self, ctx:PostgreSQLParser.Displayed_column_arrContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#exp_factor1.
    def enterExp_factor1(self, ctx:PostgreSQLParser.Exp_factor1Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#exp_factor1.
    def exitExp_factor1(self, ctx:PostgreSQLParser.Exp_factor1Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#exp_factor2.
    def enterExp_factor2(self, ctx:PostgreSQLParser.Exp_factor2Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#exp_factor2.
    def exitExp_factor2(self, ctx:PostgreSQLParser.Exp_factor2Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#exp_factor3.
    def enterExp_factor3(self, ctx:PostgreSQLParser.Exp_factor3Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#exp_factor3.
    def exitExp_factor3(self, ctx:PostgreSQLParser.Exp_factor3Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#expression.
    def enterExpression(self, ctx:PostgreSQLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#expression.
    def exitExpression(self, ctx:PostgreSQLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#expression_list.
    def enterExpression_list(self, ctx:PostgreSQLParser.Expression_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#expression_list.
    def exitExpression_list(self, ctx:PostgreSQLParser.Expression_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#factor1.
    def enterFactor1(self, ctx:PostgreSQLParser.Factor1Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#factor1.
    def exitFactor1(self, ctx:PostgreSQLParser.Factor1Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#factor2.
    def enterFactor2(self, ctx:PostgreSQLParser.Factor2Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#factor2.
    def exitFactor2(self, ctx:PostgreSQLParser.Factor2Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#factor3.
    def enterFactor3(self, ctx:PostgreSQLParser.Factor3Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#factor3.
    def exitFactor3(self, ctx:PostgreSQLParser.Factor3Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#factor4.
    def enterFactor4(self, ctx:PostgreSQLParser.Factor4Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#factor4.
    def exitFactor4(self, ctx:PostgreSQLParser.Factor4Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#factor5.
    def enterFactor5(self, ctx:PostgreSQLParser.Factor5Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#factor5.
    def exitFactor5(self, ctx:PostgreSQLParser.Factor5Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#function_call.
    def enterFunction_call(self, ctx:PostgreSQLParser.Function_callContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#function_call.
    def exitFunction_call(self, ctx:PostgreSQLParser.Function_callContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#groupby_clause.
    def enterGroupby_clause(self, ctx:PostgreSQLParser.Groupby_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#groupby_clause.
    def exitGroupby_clause(self, ctx:PostgreSQLParser.Groupby_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#groupby_item.
    def enterGroupby_item(self, ctx:PostgreSQLParser.Groupby_itemContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#groupby_item.
    def exitGroupby_item(self, ctx:PostgreSQLParser.Groupby_itemContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#having_clause.
    def enterHaving_clause(self, ctx:PostgreSQLParser.Having_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#having_clause.
    def exitHaving_clause(self, ctx:PostgreSQLParser.Having_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#index_hint.
    def enterIndex_hint(self, ctx:PostgreSQLParser.Index_hintContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#index_hint.
    def exitIndex_hint(self, ctx:PostgreSQLParser.Index_hintContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#index_hint_list.
    def enterIndex_hint_list(self, ctx:PostgreSQLParser.Index_hint_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#index_hint_list.
    def exitIndex_hint_list(self, ctx:PostgreSQLParser.Index_hint_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#index_name.
    def enterIndex_name(self, ctx:PostgreSQLParser.Index_nameContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#index_name.
    def exitIndex_name(self, ctx:PostgreSQLParser.Index_nameContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#index_list.
    def enterIndex_list(self, ctx:PostgreSQLParser.Index_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#index_list.
    def exitIndex_list(self, ctx:PostgreSQLParser.Index_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#index_options.
    def enterIndex_options(self, ctx:PostgreSQLParser.Index_optionsContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#index_options.
    def exitIndex_options(self, ctx:PostgreSQLParser.Index_optionsContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#interval_expr.
    def enterInterval_expr(self, ctx:PostgreSQLParser.Interval_exprContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#interval_expr.
    def exitInterval_expr(self, ctx:PostgreSQLParser.Interval_exprContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#join_condition.
    def enterJoin_condition(self, ctx:PostgreSQLParser.Join_conditionContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#join_condition.
    def exitJoin_condition(self, ctx:PostgreSQLParser.Join_conditionContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#limit_clause.
    def enterLimit_clause(self, ctx:PostgreSQLParser.Limit_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#limit_clause.
    def exitLimit_clause(self, ctx:PostgreSQLParser.Limit_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#offset.
    def enterOffset(self, ctx:PostgreSQLParser.OffsetContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#offset.
    def exitOffset(self, ctx:PostgreSQLParser.OffsetContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#offset_clause.
    def enterOffset_clause(self, ctx:PostgreSQLParser.Offset_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#offset_clause.
    def exitOffset_clause(self, ctx:PostgreSQLParser.Offset_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#row_count.
    def enterRow_count(self, ctx:PostgreSQLParser.Row_countContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#row_count.
    def exitRow_count(self, ctx:PostgreSQLParser.Row_countContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#orderby_clause.
    def enterOrderby_clause(self, ctx:PostgreSQLParser.Orderby_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#orderby_clause.
    def exitOrderby_clause(self, ctx:PostgreSQLParser.Orderby_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#orderby_item.
    def enterOrderby_item(self, ctx:PostgreSQLParser.Orderby_itemContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#orderby_item.
    def exitOrderby_item(self, ctx:PostgreSQLParser.Orderby_itemContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#partition_clause.
    def enterPartition_clause(self, ctx:PostgreSQLParser.Partition_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#partition_clause.
    def exitPartition_clause(self, ctx:PostgreSQLParser.Partition_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#partition_name.
    def enterPartition_name(self, ctx:PostgreSQLParser.Partition_nameContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#partition_name.
    def exitPartition_name(self, ctx:PostgreSQLParser.Partition_nameContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#partition_names.
    def enterPartition_names(self, ctx:PostgreSQLParser.Partition_namesContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#partition_names.
    def exitPartition_names(self, ctx:PostgreSQLParser.Partition_namesContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#bit_fac1.
    def enterBit_fac1(self, ctx:PostgreSQLParser.Bit_fac1Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#bit_fac1.
    def exitBit_fac1(self, ctx:PostgreSQLParser.Bit_fac1Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#bit_fac2.
    def enterBit_fac2(self, ctx:PostgreSQLParser.Bit_fac2Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#bit_fac2.
    def exitBit_fac2(self, ctx:PostgreSQLParser.Bit_fac2Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#predicate.
    def enterPredicate(self, ctx:PostgreSQLParser.PredicateContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#predicate.
    def exitPredicate(self, ctx:PostgreSQLParser.PredicateContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#query.
    def enterQuery(self, ctx:PostgreSQLParser.QueryContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#query.
    def exitQuery(self, ctx:PostgreSQLParser.QueryContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#schema_name.
    def enterSchema_name(self, ctx:PostgreSQLParser.Schema_nameContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#schema_name.
    def exitSchema_name(self, ctx:PostgreSQLParser.Schema_nameContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#select_list.
    def enterSelect_list(self, ctx:PostgreSQLParser.Select_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#select_list.
    def exitSelect_list(self, ctx:PostgreSQLParser.Select_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#subselect_list.
    def enterSubselect_list(self, ctx:PostgreSQLParser.Subselect_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#subselect_list.
    def exitSubselect_list(self, ctx:PostgreSQLParser.Subselect_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#select_statement.
    def enterSelect_statement(self, ctx:PostgreSQLParser.Select_statementContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#select_statement.
    def exitSelect_statement(self, ctx:PostgreSQLParser.Select_statementContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#simple_expr.
    def enterSimple_expr(self, ctx:PostgreSQLParser.Simple_exprContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#simple_expr.
    def exitSimple_expr(self, ctx:PostgreSQLParser.Simple_exprContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#slice_spec.
    def enterSlice_spec(self, ctx:PostgreSQLParser.Slice_specContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#slice_spec.
    def exitSlice_spec(self, ctx:PostgreSQLParser.Slice_specContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#subquery.
    def enterSubquery(self, ctx:PostgreSQLParser.SubqueryContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#subquery.
    def exitSubquery(self, ctx:PostgreSQLParser.SubqueryContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_atom.
    def enterTable_atom(self, ctx:PostgreSQLParser.Table_atomContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_atom.
    def exitTable_atom(self, ctx:PostgreSQLParser.Table_atomContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_name.
    def enterTable_name(self, ctx:PostgreSQLParser.Table_nameContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_name.
    def exitTable_name(self, ctx:PostgreSQLParser.Table_nameContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_factor1.
    def enterTable_factor1(self, ctx:PostgreSQLParser.Table_factor1Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_factor1.
    def exitTable_factor1(self, ctx:PostgreSQLParser.Table_factor1Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_factor2.
    def enterTable_factor2(self, ctx:PostgreSQLParser.Table_factor2Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_factor2.
    def exitTable_factor2(self, ctx:PostgreSQLParser.Table_factor2Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_factor3.
    def enterTable_factor3(self, ctx:PostgreSQLParser.Table_factor3Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_factor3.
    def exitTable_factor3(self, ctx:PostgreSQLParser.Table_factor3Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_factor4.
    def enterTable_factor4(self, ctx:PostgreSQLParser.Table_factor4Context):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_factor4.
    def exitTable_factor4(self, ctx:PostgreSQLParser.Table_factor4Context):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_reference.
    def enterTable_reference(self, ctx:PostgreSQLParser.Table_referenceContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_reference.
    def exitTable_reference(self, ctx:PostgreSQLParser.Table_referenceContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_references.
    def enterTable_references(self, ctx:PostgreSQLParser.Table_referencesContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_references.
    def exitTable_references(self, ctx:PostgreSQLParser.Table_referencesContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#table_spec.
    def enterTable_spec(self, ctx:PostgreSQLParser.Table_specContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#table_spec.
    def exitTable_spec(self, ctx:PostgreSQLParser.Table_specContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#values_list.
    def enterValues_list(self, ctx:PostgreSQLParser.Values_listContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#values_list.
    def exitValues_list(self, ctx:PostgreSQLParser.Values_listContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#where_clause.
    def enterWhere_clause(self, ctx:PostgreSQLParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#where_clause.
    def exitWhere_clause(self, ctx:PostgreSQLParser.Where_clauseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#pg_sphere_op.
    def enterPg_sphere_op(self, ctx:PostgreSQLParser.Pg_sphere_opContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#pg_sphere_op.
    def exitPg_sphere_op(self, ctx:PostgreSQLParser.Pg_sphere_opContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sbit_expr.
    def enterSbit_expr(self, ctx:PostgreSQLParser.Sbit_exprContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sbit_expr.
    def exitSbit_expr(self, ctx:PostgreSQLParser.Sbit_exprContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#polygon.
    def enterPolygon(self, ctx:PostgreSQLParser.PolygonContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#polygon.
    def exitPolygon(self, ctx:PostgreSQLParser.PolygonContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#point.
    def enterPoint(self, ctx:PostgreSQLParser.PointContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#point.
    def exitPoint(self, ctx:PostgreSQLParser.PointContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoint.
    def enterSpoint(self, ctx:PostgreSQLParser.SpointContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoint.
    def exitSpoint(self, ctx:PostgreSQLParser.SpointContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#scircle.
    def enterScircle(self, ctx:PostgreSQLParser.ScircleContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#scircle.
    def exitScircle(self, ctx:PostgreSQLParser.ScircleContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sline.
    def enterSline(self, ctx:PostgreSQLParser.SlineContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sline.
    def exitSline(self, ctx:PostgreSQLParser.SlineContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sellipse.
    def enterSellipse(self, ctx:PostgreSQLParser.SellipseContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sellipse.
    def exitSellipse(self, ctx:PostgreSQLParser.SellipseContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sbox.
    def enterSbox(self, ctx:PostgreSQLParser.SboxContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sbox.
    def exitSbox(self, ctx:PostgreSQLParser.SboxContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoly.
    def enterSpoly(self, ctx:PostgreSQLParser.SpolyContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoly.
    def exitSpoly(self, ctx:PostgreSQLParser.SpolyContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spath.
    def enterSpath(self, ctx:PostgreSQLParser.SpathContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spath.
    def exitSpath(self, ctx:PostgreSQLParser.SpathContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#strans.
    def enterStrans(self, ctx:PostgreSQLParser.StransContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#strans.
    def exitStrans(self, ctx:PostgreSQLParser.StransContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoint_to_array.
    def enterSpoint_to_array(self, ctx:PostgreSQLParser.Spoint_to_arrayContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoint_to_array.
    def exitSpoint_to_array(self, ctx:PostgreSQLParser.Spoint_to_arrayContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoint_to_array_deg.
    def enterSpoint_to_array_deg(self, ctx:PostgreSQLParser.Spoint_to_array_degContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoint_to_array_deg.
    def exitSpoint_to_array_deg(self, ctx:PostgreSQLParser.Spoint_to_array_degContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sbox_to_array.
    def enterSbox_to_array(self, ctx:PostgreSQLParser.Sbox_to_arrayContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sbox_to_array.
    def exitSbox_to_array(self, ctx:PostgreSQLParser.Sbox_to_arrayContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#sbox_to_array_deg.
    def enterSbox_to_array_deg(self, ctx:PostgreSQLParser.Sbox_to_array_degContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#sbox_to_array_deg.
    def exitSbox_to_array_deg(self, ctx:PostgreSQLParser.Sbox_to_array_degContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#scircle_to_array.
    def enterScircle_to_array(self, ctx:PostgreSQLParser.Scircle_to_arrayContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#scircle_to_array.
    def exitScircle_to_array(self, ctx:PostgreSQLParser.Scircle_to_arrayContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#scircle_to_array_deg.
    def enterScircle_to_array_deg(self, ctx:PostgreSQLParser.Scircle_to_array_degContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#scircle_to_array_deg.
    def exitScircle_to_array_deg(self, ctx:PostgreSQLParser.Scircle_to_array_degContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoly_to_array.
    def enterSpoly_to_array(self, ctx:PostgreSQLParser.Spoly_to_arrayContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoly_to_array.
    def exitSpoly_to_array(self, ctx:PostgreSQLParser.Spoly_to_arrayContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#spoly_to_array_deg.
    def enterSpoly_to_array_deg(self, ctx:PostgreSQLParser.Spoly_to_array_degContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#spoly_to_array_deg.
    def exitSpoly_to_array_deg(self, ctx:PostgreSQLParser.Spoly_to_array_degContext):
        pass


    # Enter a parse tree produced by PostgreSQLParser#pg_sphere_object.
    def enterPg_sphere_object(self, ctx:PostgreSQLParser.Pg_sphere_objectContext):
        pass

    # Exit a parse tree produced by PostgreSQLParser#pg_sphere_object.
    def exitPg_sphere_object(self, ctx:PostgreSQLParser.Pg_sphere_objectContext):
        pass



del PostgreSQLParser