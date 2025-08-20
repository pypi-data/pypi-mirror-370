import pandas as pd
from fastapi import APIRouter
from loguru import logger as log
from pandas import DataFrame
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, HTMLResponse
from toomanysessions import SessionedServer
from toomanythreads import ThreadedServer

from . import Database, CWD_TEMPLATER


class JSON(APIRouter):
    def __init__(self, server):
        super().__init__()
        self.server: 'API' = server
        self.db = self.server.db

        @self.get("/json/{table}")
        def table(table: str):
            try:
                df: DataFrame = getattr(self.db, table)
                return JSONResponse(df.to_json())
            except Exception as e:
                return Response(str(e), status_code=404)

        @self.get("/json/{table}/{index}")
        async def row(table, index):
            try:
                df: DataFrame = getattr(self.db, table)
                row = df.loc[index]
                return JSONResponse(row.to_json())
            except Exception as e:
                return Response(str(e), status_code=404)

        @self.get("/json/{table}/filter")
        async def filter_table(table, column: str = None, value: str = None, operator: str = "eq"):
            try:
                df: DataFrame = getattr(self.db, table)
                if not column or not value:
                    return JSONResponse(df.to_json())

                if column not in df.columns:
                    raise KeyError("Column not found!")
                if operator == "eq":
                    filtered_df = df[df[column] == value]
                elif operator == "ne":
                    filtered_df = df[df[column] != value]
                elif operator == "gt":
                    filtered_df = df[df[column] > float(value)]
                elif operator == "lt":
                    filtered_df = df[df[column] < float(value)]
                elif operator == "gte":
                    filtered_df = df[df[column] >= float(value)]
                elif operator == "lte":
                    filtered_df = df[df[column] <= float(value)]
                elif operator == "contains":
                    filtered_df = df[df[column].str.contains(value, na=False)]
                else:
                    raise TypeError("Invalid operator")
                return JSONResponse(filtered_df.to_json())
            except Exception as e:
                return Response(str(e), status_code=400)

        @self.get("/json/{table}/search")
        async def search_table(table, q: str):
            try:
                df: DataFrame = getattr(self.db, table)

                # Search across all string columns
                mask = df.select_dtypes(include=['object']).apply(
                    lambda x: x.str.contains(q, case=False, na=False)
                ).any(axis=1)

                filtered_df = df[mask]
                return JSONResponse(filtered_df.to_json())
            except Exception as e:
                 return Response(str(e), status_code=400)

        @self.get("/json/{table}/unique/{column}")
        async def unique_values(table, column):
            try:
                df: DataFrame = getattr(self.db, table)
                if column not in df.columns:
                    raise KeyError(f"Column '{column}' not found in table '{table}'")
                return JSONResponse(df[column].unique().tolist())
            except Exception as e:
                return Response(str(e), status_code=404)

        @self.post("/json/{table}/add")
        async def add_row(table: str, request: Request):
            """Add a new row using Database CRUD pattern"""
            try:
                data = await request.json()
                df = getattr(self.db, table)

                # Use Database context manager with DataFrame
                with self.db.table(df) as t:
                    t.create(**data)

                log.info(f"Added row to table '{table}': {data}")
                return JSONResponse({"success": True, "message": "Row added successfully"})

            except Exception as e:
                log.error(f"Error adding row to '{table}': {e}")
                return Response(f"Error adding row: {str(e)}", status_code=400)

        @self.post("/json/{table}/update/{index}")
        async def update_row(table: str, index: int, request: Request):
            """Update a specific row using Database CRUD pattern"""
            try:
                data = await request.json()
                df = getattr(self.db, table)

                if index >= len(df):
                    return Response("Index not found", status_code=404)

                # Get the current row data to create conditions
                current_row = df.iloc[index]
                conditions = current_row.to_dict()

                # Use Database context manager with DataFrame
                with self.db.table(df) as t:
                    t.update(updates=data, **conditions)

                log.info(f"Updated row {index} in table '{table}': {data}")
                return JSONResponse({"success": True, "message": "Row updated successfully"})

            except Exception as e:
                log.error(f"Error updating row {index} in '{table}': {e}")
                return Response(f"Error updating row: {str(e)}", status_code=400)

        @self.delete("/json/{table}/{index}")
        def delete_row(table: str, index: int):
            """Delete a specific row using Database CRUD pattern"""
            try:
                df = getattr(self.db, table)

                if index >= len(df):
                    return Response("Index not found", status_code=404)

                # Get the row data to create conditions for deletion
                row_to_delete = df.iloc[index]
                conditions = row_to_delete.to_dict()

                # Use Database context manager with DataFrame
                with self.db.table(df) as t:
                    t.delete(**conditions)

                log.info(f"Deleted row {index} from table '{table}'")
                return JSONResponse({"success": True, "message": "Row deleted successfully"})

            except Exception as e:
                log.error(f"Error deleting row {index} from '{table}': {e}")
                return Response(f"Error deleting row: {str(e)}", status_code=400)

class Admin(APIRouter):
    def __init__(self, server):
        super().__init__()
        from .database import API
        self.server: API = server
        self.db = self.server.db

        @self.get("/")
        def dashboard():
            """Database dashboard showing all _tables as cards"""
            tables_info = {}
            total_rows = 0
            total_columns = 0

            for table_name in self.db._tables.keys():
                df = getattr(self.db, table_name)
                table_dict = df.analytics
                total_rows += int(table_dict.row_count)
                total_columns += int(table_dict.column_count)
                tables_info[table_name] = table_dict

            log.debug(f"{self}: Attempting to load dashboard:\n  - tables_info={tables_info}\n  - total_rows={total_rows}\n  - total_columns={total_columns}")
            resp = self.server.templater.safe_render(
                'admin_dashboard.html',
                tables = tables_info,
                total_rows = total_rows,
                total_columns = total_columns
            )
            return resp

        @self.get("/{table}/card")
        async def table_card(table: str):
            """Returns a single table card HTML fragment"""
            try:
                df = getattr(self.db, table)

                return self.server.templater.safe_render(
                    'table_card.html',
                    table_name=table,
                    row_count=df.analytics.row_count,
                    column_count=df.analytics.column_count,
                    size=f"{df.analytics.size_kilobytes} KB",
                    description=f"No description"
                )

            except Exception as e:
                log.error(f"Error loading table card for '{table}': {e}")
                return self.server.templater.safe_render(
                    'table_card.html',
                    table_name=table,
                    row_count=0,
                    column_count=0,
                    size="Error",
                    description="Error loading table"
                )

        @self.get("/{table}")
        async def table_detail(table: str):
            """Table detail page showing row cards"""
            try:
                # Get the table DataFrame
                if table not in self.db._tables:
                    return Response(f"Table '{table}' not found", status_code=404)

                df = self.db._tables[table]
                if df is None:
                    return Response(f"Table '{table}' is empty", status_code=404)

                # Get table info
                columns = list(df.columns)
                total_rows = int(len(df))
                initial_load = 20  # Number of cards to load initially
                actual_load = min(initial_load, total_rows)  # Don't load more than we have

                # Define default columns to exclude from user forms
                default_columns = ['created_at', 'created_by', 'modified_at', 'modified_by']

                # Get column info for the add form (excluding default columns)
                column_info = []
                for col in columns:
                    # Skip default columns in the add form
                    if col in default_columns:
                        log.debug(f"Skipping default column {col} from add form")
                        continue

                    dtype = str(df[col].dtype)
                    if 'int' in dtype or 'float' in dtype:
                        input_type = 'number'
                    elif 'datetime' in dtype:
                        input_type = 'datetime-local'
                    elif 'bool' in dtype:
                        input_type = 'checkbox'
                    else:
                        input_type = 'text'

                    column_info.append({
                        'name': col,
                        'type': input_type
                    })

                template_data = {
                    'table_name': table,
                    'columns': columns,  # Keep all columns for display purposes
                    'column_info': column_info,  # Filtered list for the add form
                    'total_rows': total_rows,
                    'initial_load': initial_load,
                    'actual_load': actual_load
                }

                return self.server.templater.safe_render('table_detail.html', **template_data)

            except Exception as e:
                log.error(f"Error loading table detail for '{table}': {e}")
                return Response(f"Error loading table: {str(e)}", status_code=500)

        @self.get("/{table}/search")
        async def table_search(table: str, request: Request):
            """Returns a list of card URLs for filtered rows"""
            try:
                log.debug(f"Searching table: {table}")

                # Get the table DataFrame
                if table not in self.db._tables:
                    log.error(f"Table '{table}' not found")
                    return Response(f"Table '{table}' not found", status_code=404)

                df = self.db._tables[table]
                if df is None:
                    log.warning(f"Table '{table}' is empty")
                    return HTMLResponse('<div class="empty-state"><div class="empty-icon">📄</div><h3>No Rows Found</h3><p>This table is empty.</p></div>')

                # Get search parameters
                search_query = request.query_params.get('search', '').strip()
                column_filter = request.query_params.get('column', '').strip()

                log.debug(f"Search parameters - query: '{search_query}', column: '{column_filter}'")

                # Apply filtering
                filtered_df = df.copy()

                if search_query:
                    if column_filter and column_filter in df.columns:
                        # Search in specific column
                        log.debug(f"Searching in column '{column_filter}' for '{search_query}'")
                        mask = filtered_df[column_filter].astype(str).str.contains(search_query, case=False, na=False)
                        filtered_df = filtered_df[mask]
                    else:
                        # Search across all string columns
                        log.debug(f"Searching across all columns for '{search_query}'")
                        mask = filtered_df.select_dtypes(include=['object']).apply(
                            lambda x: x.astype(str).str.contains(search_query, case=False, na=False)
                        ).any(axis=1)

                        # Also search numeric columns converted to string
                        numeric_mask = filtered_df.select_dtypes(include=['number']).apply(
                            lambda x: x.astype(str).str.contains(search_query, case=False, na=False)
                        ).any(axis=1)

                        combined_mask = mask | numeric_mask
                        filtered_df = filtered_df[combined_mask]

                log.info(f"Filtered results: {len(filtered_df)} rows (from {len(df)} total)")

                # If no results found
                if len(filtered_df) == 0:
                    if search_query:
                        return HTMLResponse('''
                        <div class="empty-state">
                            <div class="empty-icon">🔍</div>
                            <h3>No Results Found</h3>
                            <p>No rows match your search criteria.</p>
                        </div>
                        ''')
                    else:
                        return HTMLResponse('''
                        <div class="empty-state">
                            <div class="empty-icon">📄</div>
                            <h3>No Rows Found</h3>
                            <p>This table is empty.</p>
                        </div>
                        ''')

                # Build list of card placeholder divs with HTMX requests
                card_divs = []

                for idx in filtered_df.index:
                    try:
                        # Get original DataFrame index position
                        original_index = df.index.get_loc(idx)

                        # Create placeholder div with HTMX request to individual card endpoint
                        card_div = f'''
                        <div
                            hx-get="/{table}/{original_index}/card"
                            hx-trigger="load"
                            hx-swap="outerHTML"
                            data-row-index="{original_index}"
                            data-table-name="{table}"
                        >
                            <div class="loading-container">
                                <div class="loading-spinner"></div>
                            </div>
                        </div>'''

                        card_divs.append(card_div)

                    except Exception as e:
                        log.error(f"Error creating card placeholder for row {idx}: {e}")
                        # Add error card directly
                        error_card = f'''
                        <div class="card row-card" data-row-index="{idx}" data-table-name="{table}" style="border-color: #dc2626;">
                            <div class="icon small" style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
                                <div class="icon-content">⚠️</div>
                            </div>
                            <h3>Row {idx}</h3>
                            <p class="subtitle" style="color: #dc2626;">Error loading row</p>
                        </div>
                        '''
                        card_divs.append(error_card)

                # Return all card placeholder divs
                final_html = '\n'.join(card_divs)
                log.debug(f"Returning {len(card_divs)} card placeholders for client to load")

                return HTMLResponse(final_html)

            except Exception as e:
                log.error(f"Error searching table '{table}': {e}")
                return HTMLResponse(f'''
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Error Searching Table</h3>
                    <p>Error: {str(e)}</p>
                </div>
                ''')

        @self.get("/{table}/{index}/card")
        async def row_card(table: str, index: int):
            """Returns a single row card HTML fragment"""
            try:
                df = getattr(self.db, table)
                if not getattr(df, "get_title", None):
                    self.db._fetch()
                    df = getattr(self.db, table)
                if index >= len(df) or index < 0: return Response(f"Row {index} not found in table '{table}'", status_code=404)

                try: title = df.get_title(index)
                except Exception: title = ""

                try: subtitle = df.get_subtitle(index)
                except Exception: subtitle = ""


                if not (title or subtitle):
                    log.error("Failed to get title or subtitle after fetch attempt")
                    raise RuntimeError("Could not retrieve title or subtitle")
                # Get row data and handle NaN/None values
                columns = list(df.columns)
                row_series = df.iloc[index]

                # Convert to dict and handle NaN values
                row_data = {
                    'title': title,
                    'subtitle': subtitle,
                    'index': index
                }
                for col in columns:
                    value = row_series[col]
                    if pd.isna(value):
                        row_data[col] = ""
                    else:
                        row_data[col] = str(value)


                # Prepare template data
                template_data = {
                    'table_name': table,
                    'row_index': index,
                    'columns': columns,
                    'row_data': row_data,
                    'preview_columns': columns[:4]  # First 4 columns for preview
                }

                return self.server.templater.safe_render('row_card.html', **template_data)

            except Exception as e:
                log.error(f"Error loading row card for '{table}' index {index}: {e}")

                # Return error card
                error_html = f'''
                <div class="card row-card" data-row-index="{index}" data-table-name="{table}" style="border-color: #dc2626;">
                    <div class="icon small" style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
                        <div class="icon-content">⚠️</div>
                    </div>
                    <h3>Row {index}</h3>
                    <p class="subtitle" style="color: #dc2626;">Error loading row</p>
                </div>
                '''
                return HTMLResponse(error_html)

        @self.get("/{table}/{index}")
        async def row_detail(table: str, index: int):
            """Row detail page showing individual row data with edit capability"""
            try:
                # Get the table DataFrame
                if table not in self.db._tables:
                    return Response(f"Table '{table}' not found", status_code=404)

                df = getattr(self.db, table)
                if df is None:
                    return Response(f"Table '{table}' is empty", status_code=404)

                # Check if row exists
                if index >= len(df) or index < 0:
                    return Response(f"Row {index} not found in table '{table}'", status_code=404)

                # Get row data and handle NaN/None values
                all_columns = list(df.columns)
                row_series = df.iloc[index]

                # Convert to dict and handle NaN values
                all_row_data = {}
                for col in all_columns:
                    value = row_series[col]
                    if pd.isna(value):
                        all_row_data[col] = ""
                    else:
                        all_row_data[col] = str(value)

                # Split columns - first 4 for header, rest for main display
                header_columns = all_columns[:4] if len(all_columns) >= 4 else []
                display_columns = all_columns[4:] if len(all_columns) >= 4 else all_columns

                # Create header data and display data
                header_data = {}
                for col in header_columns:
                    value = all_row_data[col]
                    if col in ['created_at', 'modified_at'] and value:
                        try:
                            # Parse the datetime string and reformat it
                            from datetime import datetime
                            dt = datetime.fromisoformat(value.replace(' ', 'T') if ' ' in value else value)
                            value = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            # If parsing fails, keep original value
                            pass
                    header_data[col] = value

                row_data = {col: all_row_data[col] for col in display_columns}

                # Get column info for the edit form (only for display columns)
                column_info = []
                for col in display_columns:
                    dtype = str(df[col].dtype)
                    if 'int' in dtype or 'float' in dtype:
                        input_type = 'number'
                    elif 'datetime' in dtype:
                        input_type = 'datetime-local'
                    elif 'bool' in dtype:
                        input_type = 'checkbox'
                    else:
                        input_type = 'text'

                    column_info.append({
                        'name': col,
                        'type': input_type
                    })

                template_data = {
                    'table_name': table,
                    'row_index': index,
                    'columns': display_columns,
                    'column_info': column_info,
                    'row_data': row_data,
                    'header_data': header_data
                }

                # Render row detail template
                return self.server.templater.safe_render('row_detail.html', **template_data)

            except Exception as e:
                log.error(f"Error loading row detail for '{table}' index {index}: {e}")
                return Response(f"Error loading row: {str(e)}", status_code=500)