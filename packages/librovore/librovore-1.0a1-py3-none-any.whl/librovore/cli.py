# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Command-line interface. '''


from . import __
from . import cacheproxy as _cacheproxy
from . import exceptions as _exceptions
from . import functions as _functions
from . import interfaces as _interfaces
from . import server as _server
from . import state as _state


_scribe = __.acquire_scribe( __name__ )


GroupByArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'group by argument' ) ),
]
IncludeSnippets: __.typx.TypeAlias = __.typx.Annotated[
    bool,
    __.tyro.conf.arg( help = __.access_doctab( 'include snippets argument' ) ),
]
PortArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ int ],
    __.tyro.conf.arg( help = __.access_doctab( 'server port argument' ) ),
]
TermArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'term argument' ) ),
]
ResultsMax: __.typx.TypeAlias = __.typx.Annotated[
    int,
    __.tyro.conf.arg( help = __.access_doctab( 'results max argument' ) ),
]
LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'location argument' ) ),
]
TransportArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'transport argument' ) ),
]


_search_behaviors_default = _interfaces.SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )

_MARKDOWN_OBJECT_LIMIT = 10
_MARKDOWN_CONTENT_LIMIT = 200



class _CliCommand(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' CLI command. '''

    @__.abc.abstractmethod
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        ''' Executes command with global state. '''
        raise NotImplementedError


class DetectCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Detect which processors can handle a documentation source. '''

    location: LocationArgument
    genus: __.typx.Annotated[
        _interfaces.ProcessorGenera,
        __.tyro.conf.arg( help = "Processor genus (inventory or structure)." ),
    ]
    processor_name: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg( help = "Specific processor to use." ),
    ] = None

    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        processor_name = (
            self.processor_name if self.processor_name is not None
            else __.absent )
        try:
            result = await _functions.detect(
                auxdata, self.location, self.genus,
                processor_name = processor_name )
        except Exception as exc:
            _scribe.error( "detect failed: %s", exc )
            print( _format_cli_exception( exc ), file = stream )
            raise SystemExit( 1 ) from None
        output = _format_output( result, display_format )
        print( output, file = stream )


class QueryInventoryCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Searches object inventory by name with fuzzy matching. '''

    location: LocationArgument
    term: TermArgument
    details: __.typx.Annotated[
        _interfaces.InventoryQueryDetails,
        __.tyro.conf.arg(
            help = __.access_doctab( 'query details argument' ) ),
    ] = _interfaces.InventoryQueryDetails.Documentation
    filters: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = lambda: dict( _filters_default ) )
    search_behaviors: __.typx.Annotated[
        _interfaces.SearchBehaviors,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field(
        default_factory = lambda: _interfaces.SearchBehaviors( ) )
    results_max: __.typx.Annotated[
        int,
        __.tyro.conf.arg( help = __.access_doctab( 'results max argument' ) ),
    ] = 5

    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        try:
            result = await _functions.query_inventory(
                auxdata,
                self.location,
                self.term,
                search_behaviors = self.search_behaviors,
                filters = self.filters,
                results_max = self.results_max,
                details = self.details )
        except Exception as exc:
            _scribe.error( "query-inventory failed: %s", exc )
            print( _format_cli_exception( exc ), file = stream )
            raise SystemExit( 1 ) from None
        output = _format_output( result, display_format )
        print( output, file = stream )


class QueryContentCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Searches documentation content with relevance ranking and snippets. '''

    location: LocationArgument
    term: TermArgument
    search_behaviors: __.typx.Annotated[
        _interfaces.SearchBehaviors,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field(
        default_factory = lambda: _interfaces.SearchBehaviors( ) )
    filters: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = lambda: dict( _filters_default ) )
    include_snippets: IncludeSnippets = True
    results_max: ResultsMax = 10
    lines_max: __.typx.Annotated[
        int,
        __.tyro.conf.arg(
            help = "Maximum number of lines to display per result." ),
    ] = 40

    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        try:
            result = await _functions.query_content(
                auxdata, self.location, self.term,
                search_behaviors = self.search_behaviors,
                filters = self.filters,
                results_max = self.results_max,
                include_snippets = self.include_snippets )
        except Exception as exc:
            _scribe.error( "query-content failed: %s", exc )
            print( _format_cli_exception( exc ), file = stream )
            raise SystemExit( 1 ) from None
        # Apply lines_max truncation to content
        if 'documents' in result and self.lines_max > 0:
            result = _truncate_query_content( result, self.lines_max )
        output = _format_output( result, display_format )
        print( output, file = stream )


class SummarizeInventoryCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Provides human-readable summary of inventory. '''

    location: LocationArgument
    term: TermArgument = ''
    filters: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = lambda: dict( _filters_default ) )
    group_by: GroupByArgument = None
    search_behaviors: __.typx.Annotated[
        _interfaces.SearchBehaviors,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field(
        default_factory = lambda: _interfaces.SearchBehaviors( ) )

    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        result = await _functions.summarize_inventory(
            auxdata, self.location, self.term or '',
            search_behaviors = self.search_behaviors,
            filters = self.filters,
            group_by = self.group_by )
        output = _format_output( result, display_format )
        print( output, file = stream )


class SurveyProcessorsCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' List processors for specified genus and their capabilities. '''

    genus: __.typx.Annotated[
        _interfaces.ProcessorGenera,
        __.tyro.conf.arg( help = "Processor genus (inventory or structure)." ),
    ]
    name: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg( help = "Name of processor to describe" ),
    ] = None

    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        nomargs: __.NominativeArguments = { 'genus': self.genus }
        if self.name is not None: nomargs[ 'name' ] = self.name
        try:
            result = await _functions.survey_processors( auxdata, **nomargs )
        except Exception as exc:
            _scribe.error( "survey-processors failed: %s", exc )
            print( _format_cli_exception( exc ), file = stream )
            raise SystemExit( 1 ) from None
        output = _format_output( result, display_format )
        print( output, file = stream )



class ServeCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Starts MCP server. '''

    port: PortArgument = None
    transport: TransportArgument = None
    extra_functions: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Enable extra functions (detect and survey-processors)." ),
    ] = False
    serve_function: __.typx.Callable[
        [ _state.Globals ], __.cabc.Awaitable[ None ]
    ] = _server.serve
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        nomargs: __.NominativeArguments = { }
        if self.port is not None: nomargs[ 'port' ] = self.port
        if self.transport is not None: nomargs[ 'transport' ] = self.transport
        nomargs[ 'extra_functions' ] = self.extra_functions
        await self.serve_function( auxdata, **nomargs )


class Cli( __.immut.DataclassObject, decorators = ( __.simple_tyro_class, ) ):
    ''' MCP server CLI. '''

    display: __.DisplayTarget
    display_format: __.typx.Annotated[
        _interfaces.DisplayFormat,
        __.tyro.conf.arg( help = "Output format for command results." ),
    ] = _interfaces.DisplayFormat.Markdown
    command: __.typx.Union[
        __.typx.Annotated[
            DetectCommand,
            __.tyro.conf.subcommand( 'detect', prefix_name = False ),
        ],
        __.typx.Annotated[
            QueryInventoryCommand,
            __.tyro.conf.subcommand( 'query-inventory', prefix_name = False ),
        ],
        __.typx.Annotated[
            QueryContentCommand,
            __.tyro.conf.subcommand( 'query-content', prefix_name = False ),
        ],
        __.typx.Annotated[
            SummarizeInventoryCommand,
            __.tyro.conf.subcommand(
                'summarize-inventory', prefix_name = False ),
        ],
        __.typx.Annotated[
            SurveyProcessorsCommand,
            __.tyro.conf.subcommand(
                'survey-processors', prefix_name = False ),
        ],
        __.typx.Annotated[
            ServeCommand,
            __.tyro.conf.subcommand( 'serve', prefix_name = False ),
        ],
    ]
    logfile: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc( ''' Path to log capture file. ''' ),
    ] = None

    async def __call__( self ):
        ''' Invokes command after library preparation. '''
        nomargs = self.prepare_invocation_args( )
        async with __.ctxl.AsyncExitStack( ) as exits:
            auxdata = await _prepare( exits = exits, **nomargs )
            from . import xtnsmgr
            await xtnsmgr.register_processors( auxdata )
            await self.command(
                auxdata = auxdata,
                display = self.display,
                display_format = self.display_format )

    def prepare_invocation_args(
        self,
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Prepares arguments for initial configuration. '''
        args: dict[ str, __.typx.Any ] = dict(
            environment = True,
            logfile = self.logfile,
        )
        return args


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    config = (
        __.tyro.conf.HelptextFromCommentsOff,
    )
    with __.warnings.catch_warnings( ):
        __.warnings.filterwarnings(
            'ignore',
            message = r'Mutable type .* is used as a default value.*',
            category = UserWarning,
            module = 'tyro.constructors._struct_spec_dataclass' )
        try: __.asyncio.run( __.tyro.cli( Cli, config = config )( ) )
        except SystemExit: raise
        except BaseException as exc:
            __.report_exceptions( exc, _scribe )
            raise SystemExit( 1 ) from None


def _extract_object_name_and_role( obj: __.typx.Any ) -> tuple[ str, str ]:
    ''' Extracts name and role from object, with safe fallbacks. '''
    if not hasattr( obj, 'get' ):
        return 'Unknown', 'unknown'
    try:
        name = getattr( obj, 'get' )( 'name', 'Unknown' )
    except ( AttributeError, TypeError ):
        name = 'Unknown'
    try:
        role = getattr( obj, 'get' )( 'role', 'unknown' )
    except ( AttributeError, TypeError ):
        role = 'unknown'
    if not isinstance( name, str ):
        name = str( name ) if name is not None else 'Unknown'
    if not isinstance( role, str ):
        role = str( role ) if role is not None else 'unknown'
    return name, role


def _format_as_markdown( result: __.cabc.Mapping[ str, __.typx.Any ] ) -> str:
    ''' Converts structured data to Markdown format. '''
    if 'project' in result and 'version' in result and 'objects' in result:
        return _format_inventory_summary_markdown( result )
    if 'documents' in result and 'search_metadata' in result:
        return _format_query_result_markdown( result )
    if 'source' in result and 'detections' in result:
        return _format_detect_result_markdown( result )
    return __.json.dumps( result, indent = 2 )


def _format_detect_result_markdown(
    result: __.cabc.Mapping[ str, __.typx.Any ]
) -> str:
    ''' Formats detection results as Markdown. '''
    source = result.get( 'source', 'Unknown' )
    optimal = result.get( 'detection_optimal' )
    time_ms = result.get( 'time_detection_ms', 0 )
    lines = [
        "# Detection Results",
        f"**Source:** {source}",
        f"**Detection Time:** {time_ms}ms",
    ]
    if optimal:
        processor = optimal.get( 'processor', {} )
        confidence = optimal.get( 'confidence', 0 )
        lines.extend([
            "\n## Optimal Processor",
            f"- **Name:** {processor.get('name', 'Unknown')}",
            f"- **Confidence:** {confidence:.1%}",
        ])
    return '\n'.join( lines )


def _format_grouped_objects( 
    objects_value: __.cabc.Mapping[ str, __.typx.Any ] 
) -> list[ str ]:
    ''' Formats objects grouped by categories. '''
    lines: list[ str ] = [ "\n## Breakdown by Groups" ]
    for group_name, group_objects in objects_value.items( ):
        if hasattr( group_objects, '__len__' ):
            object_count = len( group_objects )
            lines.append( f"- **{group_name}:** {object_count} objects" )
    return lines


def _format_inventory_summary_markdown(
    result: __.cabc.Mapping[ str, __.typx.Any ]
) -> str:
    ''' Formats inventory summary as Markdown. '''
    lines = [
        f"# {result[ 'project' ]}",
        f"**Version:** {result[ 'version' ]}",
        f"**Objects:** {result[ 'objects_count' ]}",
    ]
    objects_value = result.get( 'objects' )
    if objects_value:
        if isinstance( objects_value, dict ):
            grouped_objects = __.typx.cast(
                __.cabc.Mapping[ str, __.typx.Any ], objects_value )
            lines.extend( _format_grouped_objects( grouped_objects ) )
        else:
            lines.extend( _format_object_list( objects_value ) )
    return '\n'.join( lines )


def _format_object_list( objects_value: __.typx.Any ) -> list[ str ]:
    ''' Formats a flat list of objects. '''
    lines: list[ str ] = [ ]
    if not hasattr( objects_value, '__len__' ): return lines
    objects_count = len( objects_value )
    lines.append( f"\n## Objects ({objects_count})" )
    if ( hasattr( objects_value, '__getitem__' )
         and hasattr( objects_value, '__iter__' ) ):
        subset_limit = _MARKDOWN_OBJECT_LIMIT
        objects_subset = (
            objects_value[ :subset_limit ]
            if objects_count > subset_limit else objects_value )
        for obj in objects_subset:
            name, role = _extract_object_name_and_role( obj )
            lines.append( f"- `{name}` ({role})" )
        if objects_count > _MARKDOWN_OBJECT_LIMIT:
            remaining = objects_count - _MARKDOWN_OBJECT_LIMIT
            lines.append( f"- ... and {remaining} more" )
    return lines


def _truncate_query_content(
    result: __.cabc.Mapping[ str, __.typx.Any ],
    lines_max: int,
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    ''' Truncates content in query results to specified line limit. '''
    truncated_docs: list[ __.cabc.Mapping[ str, __.typx.Any ] ] = []
    for doc in result[ 'documents' ]:
        truncated_doc = dict( doc )
        if 'description' in truncated_doc:
            lines = truncated_doc[ 'description' ].split( '\n' )
            if len( lines ) > lines_max:
                truncated_lines = lines[ :lines_max ]
                truncated_lines.append( '...' )
                truncated_doc[ 'description' ] = '\n'.join( truncated_lines )
        truncated_docs.append( truncated_doc )
    result = dict( result )
    result[ 'documents' ] = truncated_docs
    return result


def _format_output(
    result: __.cabc.Mapping[ str, __.typx.Any ],
    display_format: _interfaces.DisplayFormat,
) -> str:
    ''' Formats command output according to display format. '''
    if display_format == _interfaces.DisplayFormat.JSON:
        # Serialize frigid objects to JSON-compatible format
        serialized_result = _functions.serialize_for_json( result )
        return __.json.dumps( serialized_result, indent = 2 )
    if display_format == _interfaces.DisplayFormat.Markdown:
        return _format_as_markdown( result )
    raise ValueError


def _format_query_result_markdown(
    result: __.cabc.Mapping[ str, __.typx.Any ]
) -> str:
    ''' Formats query results as Markdown. '''
    project = result.get( 'project', 'Unknown' )
    query = result.get( 'query', 'Unknown' )
    documents = result.get( 'documents', [] )
    metadata = result.get( 'search_metadata', {} )
    lines = [
        f"# Query Results: {query}",
        f"**Project:** {project}",
        f"**Results:** {metadata.get('results_count', 0)}/"
        f"{metadata.get('matches_total', 0)}",
    ]
    if documents:
        lines.append( "\n## Documents" )
        for index, doc in enumerate( documents, 1 ):
            # Add separator before each result
            separator = "\n\n🔍 ── Result {} ─────────────────────── 🔍\n"
            lines.append( separator.format( index ) )
            name = doc.get( 'name', 'Unknown' )
            role = doc.get( 'role', 'unknown' )
            lines.append( f"### `{name}`" )
            lines.append( f"- **Type:** {role}" )
            if 'domain' in doc:
                lines.append( f"- **Domain:** {doc['domain']}" )
            if 'description' in doc:
                lines.append( f"- **Content:** {doc['description']}" )
            lines.append( "" )
    return '\n'.join( lines )


def _format_cli_exception( exc: Exception ) -> str:  # noqa: PLR0911
    ''' Formats exceptions for user-friendly CLI output. '''
    match exc:
        case _exceptions.ProcessorInavailability( ):
            return (
                f"❌ No processor found to handle source: {exc.source}\n"
                f"💡 Verify this is a Sphinx documentation site" )
        case _exceptions.InventoryInaccessibility( ):
            return (
                f"❌ Cannot access documentation inventory: {exc.source}\n"
                f"💡 Check URL accessibility and network connection" )
        case _exceptions.DocumentationContentAbsence( ):
            return (
                f"❌ Documentation structure not recognized: {exc.url}\n"
                f"💡 This may be an unsupported Sphinx theme" )
        case _exceptions.DocumentationObjectAbsence( ):
            return (
                f"❌ Object '{exc.object_id}' not found in page: {exc.url}\n"
                f"💡 Verify the object name and try a broader search" )
        case _exceptions.InventoryInvalidity( ):
            return (
                f"❌ Invalid documentation inventory: {exc.source}\n"
                f"💡 The documentation site may be corrupted" )
        case _exceptions.DocumentationInaccessibility( ):
            return (
                f"❌ Documentation inaccessible: {exc.url}\n"
                f"💡 Check URL accessibility and network connection" )
        case _:
            return f"❌ Unexpected error: {exc}"


async def _prepare(
    environment: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Whether to configure environment. ''' )
    ],
    exits: __.typx.Annotated[
        __.ctxl.AsyncExitStack,
        __.ddoc.Doc( ''' Exit stack for resource management. ''' )
    ],
    logfile: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc( ''' Path to log capture file. ''' )
    ],
) -> __.typx.Annotated[
    _state.Globals,
    __.ddoc.Doc( ''' Configured global state. ''' )
]:
    ''' Configures application based on arguments. '''
    nomargs: __.NominativeArguments = {
        'environment': environment,
        'exits': exits,
    }
    if logfile:
        logfile_p = __.Path( logfile ).resolve( )
        ( logfile_p.parent ).mkdir( parents = True, exist_ok = True )
        logstream = exits.enter_context( logfile_p.open( 'w' ) )
        inscription = __.appcore.inscription.Control(
            level = 'debug', target = logstream )
        nomargs[ 'inscription' ] = inscription
    auxdata = await __.appcore.prepare( **nomargs )
    content_cache, probe_cache, robots_cache = _cacheproxy.prepare( auxdata )
    return _state.Globals(
        application = auxdata.application,
        configuration = auxdata.configuration,
        directories = auxdata.directories,
        distribution = auxdata.distribution,
        exits = auxdata.exits,
        content_cache = content_cache,
        probe_cache = probe_cache,
        robots_cache = robots_cache )
