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


''' Core business logic shared between CLI and MCP server. '''


from . import __
from . import detection as _detection
from . import exceptions as _exceptions
from . import interfaces as _interfaces
from . import processors as _processors
from . import search as _search
from . import state as _state


DocumentationResult: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]
SearchResult: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]
LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    str, __.ddoc.Fname( 'location argument' ) ]


_search_behaviors_default = _interfaces.SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )


def normalize_location( location: str ) -> str:
    ''' Normalizes location URL by stripping index.html. '''
    if location.endswith( '/index.html' ):
        location = location[ : -11 ]
    return location
_SUCCESS_RATE_MINIMUM = 0.1


async def detect(
    auxdata: _state.Globals,
    location: LocationArgument, /,
    genus: _interfaces.ProcessorGenera,
    processor_name: __.Absential[ str ] = __.absent,
) -> dict[ str, __.typx.Any ]:
    ''' Detects relevant processors of particular genus for location. '''
    location = normalize_location( location )
    start_time = __.time.perf_counter( )
    detections, detection_optimal = (
        await _detection.access_detections(
            auxdata, location, genus = genus ) )
    end_time = __.time.perf_counter( )
    detection_time_ms = int( ( end_time - start_time ) * 1000 )
    response = _processors.DetectionsForLocation(
        source = location,
        detections = detections,
        detection_optimal = (
            None if __.is_absent( detection_optimal ) else detection_optimal ),
        time_detection_ms = detection_time_ms )
    return _serialize_dataclass( response )


async def query_content(  # noqa: PLR0913
    auxdata: _state.Globals,
    location: LocationArgument,
    term: str, /, *,
    processor_name: __.Absential[ str ] = __.absent,
    search_behaviors: _interfaces.SearchBehaviors = _search_behaviors_default,
    filters: __.cabc.Mapping[ str, __.typx.Any ] = _filters_default,
    include_snippets: bool = True,
    results_max: int = 10,
) -> __.typx.Annotated[
    dict[ str, __.typx.Any ],
    __.ddoc.Fname( 'content query return' ) ]:
    ''' Searches documentation content with relevance ranking. '''
    location = normalize_location( location )
    idetection = await _detection.detect_inventory(
        auxdata, location, processor_name = processor_name )
    objects = await idetection.filter_inventory(
        auxdata, location,
        filters = filters,
        details = _interfaces.InventoryQueryDetails.Name )
    results = _search.filter_by_name(
        objects, term,
        match_mode = search_behaviors.match_mode,
        fuzzy_threshold = search_behaviors.fuzzy_threshold )
    candidates = [ result.object for result in results[ : results_max * 3 ] ]
    if not candidates:
        return {
            'source': location,
            'query': term,
            'search_metadata': {
                'results_count': 0,
                'results_max': results_max,
            },
            'documents': [ ],
        }
    sdetection = await _detection.detect_structure(
        auxdata, location, processor_name = processor_name )
    contents = await sdetection.extract_contents(
        auxdata, location, candidates, include_snippets = include_snippets )
    _validate_extraction_results(
        contents, candidates, sdetection.processor.name, location )
    contents_by_relevance = sorted(
        contents,
        key = lambda x: x.get( 'relevance_score', 0.0 ),
        reverse = True )
    contents_ = list( contents_by_relevance[ : results_max ] )
    search_metadata: dict[ str, __.typx.Any ] = {
        'results_count': len( contents_ ),
        'results_max': results_max,
    }
    documents = [
        {
            'name': result[ 'object_name' ],
            'type': result[ 'object_type' ],
            'domain': result[ 'domain' ],
            'priority': result[ 'priority' ],
            'url': result[ 'url' ],
            'signature': result[ 'signature' ],
            'description': result[ 'description' ],
            'content_snippet': result[ 'content_snippet' ],
            'relevance_score': result[ 'relevance_score' ],
            'match_reasons': result[ 'match_reasons' ]
        }
        for result in contents_ ]
    return {
        'source': location,
        'query': term,
        'search_metadata': search_metadata,
        'documents': documents,
    }


async def query_inventory(  # noqa: PLR0913
    auxdata: _state.Globals,
    location: LocationArgument,
    term: str, /, *,
    processor_name: __.Absential[ str ] = __.absent,
    search_behaviors: _interfaces.SearchBehaviors = _search_behaviors_default,
    filters: __.cabc.Mapping[ str, __.typx.Any ] = _filters_default,
    details: _interfaces.InventoryQueryDetails = (
        _interfaces.InventoryQueryDetails.Documentation ),
    results_max: int = 5,
) -> __.typx.Annotated[
    dict[ str, __.typx.Any ], __.ddoc.Fname( 'inventory query return' ) ]:
    ''' Searches object inventory by name.

        Returns configurable detail levels. Always includes object names
        plus requested detail flags (signatures, summaries, documentation).
    '''
    location = normalize_location( location )
    detection = await _detection.detect_inventory(
        auxdata, location, processor_name = processor_name )
    objects = await detection.filter_inventory(
        auxdata, location, filters = filters, details = details )
    results = _search.filter_by_name(
        objects, term,
        match_mode = search_behaviors.match_mode,
        fuzzy_threshold = search_behaviors.fuzzy_threshold )
    selections = [ result.object for result in results[ : results_max ] ]
    documents = [
        {
            'name': obj[ 'name' ],
            'role': obj[ 'role' ],
            'domain': obj.get( 'domain', '' ),
            'uri': obj[ 'uri' ],
            'dispname': obj[ 'dispname' ],
        }
        for obj in selections ]
    search_metadata: dict[ str, __.typx.Any ] = {
        'objects_count': len( selections ),
        'results_max': results_max,
        'matches_total': len( objects ),
    }
    return {
        'project': (
            objects[ 0 ].get( '_inventory_project', 'Unknown' )
            if objects else 'Unknown' ),
        'version': (
            objects[ 0 ].get( '_inventory_version', 'Unknown' )
            if objects else 'Unknown' ),
        'query': term,
        'documents': documents,
        'search_metadata': search_metadata,
        'objects_count': len( selections ),
        'source': location,
    }


async def summarize_inventory(  # noqa: PLR0913
    auxdata: _state.Globals,
    location: LocationArgument, /,
    term: str = '', *,
    processor_name: __.Absential[ str ] = __.absent,
    search_behaviors: _interfaces.SearchBehaviors = _search_behaviors_default,
    filters: __.cabc.Mapping[ str, __.typx.Any ] = _filters_default,
    group_by: __.typx.Optional[ str ] = None,
) -> __.typx.Annotated[
    dict[ str, __.typx.Any ], __.ddoc.Fname( 'inventory summary return' ) ]:
    ''' Provides structured summary of inventory data. '''
    details = _interfaces.InventoryQueryDetails.Name
    inventory_result = await query_inventory(
        auxdata, location, term, processor_name = processor_name,
        search_behaviors = search_behaviors, filters = filters,
        results_max = 1000,  # Large number to get all matches
        details = details )
    if group_by is not None:
        objects_data = _group_documents_by_field(
            inventory_result[ 'documents' ], group_by )
    else: objects_data = inventory_result[ 'documents' ]
    inventory_data: dict[ str, __.typx.Any ] = {
        'project': inventory_result[ 'project' ],
        'version': inventory_result[ 'version' ],
        'objects_count':
            inventory_result[ 'search_metadata' ][ 'matches_total' ],
        'objects': objects_data,
    }
    return inventory_data


async def survey_processors(
    auxdata: _state.Globals, /,
    genus: _interfaces.ProcessorGenera,
    name: __.typx.Optional[ str ] = None,
) -> dict[ str, __.typx.Any ]:
    ''' Lists processor capabilities for specified genus, filtered by name. '''
    match genus:
        case _interfaces.ProcessorGenera.Inventory:
            processors = dict( _processors.inventory_processors )
        case _interfaces.ProcessorGenera.Structure:
            processors = dict( _processors.structure_processors )
    if name is not None and name not in processors:
        raise _exceptions.ProcessorInavailability( name )
    processors_capabilities = {
        name_: _serialize_dataclass( processor.capabilities )
        for name_, processor in processors.items( )
        if name is None or name_ == name }
    return { 'processors': processors_capabilities }


def _add_object_metadata_to_results(
    selected_objects: list[ dict[ str, __.typx.Any ] ],
    result: dict[ str, __.typx.Any ],
) -> None:
    ''' Adds object metadata without documentation to results. '''
    for obj in selected_objects:
        document = _create_document_metadata( obj )
        result[ 'documents' ].append( document )


def _construct_explore_result_structure(  # noqa: PLR0913
    inventory_data: dict[ str, __.typx.Any ],
    query: str,
    selected_objects: list[ dict[ str, __.typx.Any ] ],
    results_max: int,
    search_behaviors: _interfaces.SearchBehaviors,
    filters: __.cabc.Mapping[ str, __.typx.Any ],
) -> dict[ str, __.typx.Any ]:
    ''' Builds the base result structure with metadata. '''
    search_metadata: dict[ str, __.typx.Any ] = {
        'objects_count': len( selected_objects ),
        'results_max': results_max,
        'matches_total': inventory_data[ 'objects_count' ],
    }
    result: dict[ str, __.typx.Any ] = {
        'project': inventory_data[ 'project' ],
        'version': inventory_data[ 'version' ],
        'query': query,
        'search_metadata': search_metadata,
        'documents': [ ],
    }
    return result


def _construct_query_result_structure(  # noqa: PLR0913
    source: str,
    query: str,
    raw_results: list[ __.cabc.Mapping[ str, __.typx.Any ] ],
    results_max: int,
    search_behaviors: _interfaces.SearchBehaviors,
    filters: __.cabc.Mapping[ str, __.typx.Any ],
) -> dict[ str, __.typx.Any ]:
    ''' Builds query result structure in explore format. '''
    search_metadata: dict[ str, __.typx.Any ] = {
        'results_count': len( raw_results ),
        'results_max': results_max,
    }
    documents: list[ dict[ str, __.typx.Any ] ] = [ ]
    for raw_result in raw_results:
        result_dict = dict( raw_result )
        document: dict[ str, __.typx.Any ] = {
            'name': result_dict[ 'object_name' ],
            'type': result_dict[ 'object_type' ],
            'domain': result_dict[ 'domain' ],
            'priority': result_dict[ 'priority' ],
            'url': result_dict[ 'url' ],
            'signature': result_dict[ 'signature' ],
            'description': result_dict[ 'description' ],
            'content_snippet': result_dict[ 'content_snippet' ],
            'relevance_score': result_dict[ 'relevance_score' ],
            'match_reasons': result_dict[ 'match_reasons' ]
        }
        documents.append( document )
    result: dict[ str, __.typx.Any ] = {
        'source': source,
        'query': query,
        'search_metadata': search_metadata,
        'documents': documents,
    }
    return result


def _create_document_with_docs(
    obj: dict[ str, __.typx.Any ],
    doc_result: __.cabc.Mapping[ str, __.typx.Any ],
) -> dict[ str, __.typx.Any ]:
    ''' Creates document structure with documentation content. '''
    document = _create_document_metadata( obj )
    document[ 'documentation' ] = doc_result
    return document


def _create_document_metadata(
    obj: dict[ str, __.typx.Any ]
) -> dict[ str, __.typx.Any ]:
    ''' Creates base document structure from object metadata. '''
    document = {
        'name': obj[ 'name' ],
        'role': obj[ 'role' ],
        'domain': obj.get( 'domain', '' ),
        'uri': obj[ 'uri' ],
        'dispname': obj[ 'dispname' ],
    }
    if 'fuzzy_score' in obj:
        document[ 'fuzzy_score' ] = obj[ 'fuzzy_score' ]
    return document


def _format_inventory_summary(
    inventory_data: dict[ str, __.typx.Any ]
) -> str:
    ''' Formats inventory data into human-readable summary. '''
    summary_lines: list[ str ] = [
        f"Project: {inventory_data[ 'project' ]}",
        f"Version: {inventory_data[ 'version' ]}",
        f"Objects: {inventory_data[ 'objects_count' ]}",
    ]
    if inventory_data[ 'objects' ]:
        if isinstance( inventory_data[ 'objects' ], dict ):
            summary_lines.append( "\nBreakdown by groups:" )
            grouped_objects = __.typx.cast(
                dict[ str, __.typx.Any ], inventory_data[ 'objects' ] )
            for group_name, objects in grouped_objects.items( ):
                object_count = len( objects )
                summary_lines.append(
                    f"  {group_name}: {object_count} objects" )
        else:
            objects = inventory_data[ 'objects' ]
            summary_lines.append( "\nObjects listed without grouping." )
    return '\n'.join( summary_lines )


def _group_documents_by_field(
    documents: __.cabc.Sequence[ __.cabc.Mapping[ str, __.typx.Any ] ],
    field: __.typx.Optional[ str ]
) -> __.immut.Dictionary[
    str, tuple[ __.cabc.Mapping[ str, __.typx.Any ], ... ]
]:
    ''' Groups documents by specified field for inventory format. '''
    if field is None: return __.immut.Dictionary( )
    groups: dict[ str, list[ __.cabc.Mapping[ str, __.typx.Any ] ] ] = { }
    for doc in documents:
        raw_value = doc.get( field, f"(missing {field})" )
        if isinstance( raw_value, list ):
            str_value = "[list]"
        elif isinstance( raw_value, dict ):
            str_value = "[dict]"
        elif raw_value is None or raw_value == '':
            str_value = f"(missing {field})"
        else:
            str_value = str( raw_value )
        if str_value not in groups: groups[ str_value ] = [ ]
        obj_data = {
            'name': doc[ 'name' ],
            'role': doc[ 'role' ],
            'domain': doc.get( 'domain', '' ),
            'uri': doc[ 'uri' ],
            'dispname': doc[ 'dispname' ],
        }
        if 'fuzzy_score' in doc:
            obj_data[ 'fuzzy_score' ] = doc[ 'fuzzy_score' ]
        obj = __.immut.Dictionary( obj_data )
        groups[ str_value ].append( obj )
    return __.immut.Dictionary(
        ( key, tuple( items ) ) for key, items in groups.items( ) )


def _serialize_dataclass( obj: __.typx.Any ) -> __.typx.Any:
    ''' Recursively serializes dataclass objects to JSON-compatible format. '''
    if __.dcls.is_dataclass( obj ):
        result = { }  # type: ignore[var-annotated]
        for field in __.dcls.fields( obj ):
            if field.name.startswith( '_' ):
                continue  # Skip private/internal fields
            value = getattr( obj, field.name )
            result[ field.name ] = _serialize_dataclass( value )
        return result  # type: ignore[return-value]
    if isinstance( obj, list ):
        return [ _serialize_dataclass( item ) for item in obj ]  # type: ignore[misc]
    if isinstance( obj, ( frozenset, set ) ):
        return list( obj )  # type: ignore[arg-type]
    if obj is None or isinstance( obj, ( str, int, float, bool ) ):
        return obj
    # For other objects, try to convert to string
    return str( obj )


def _select_top_objects(
    inventory_data: dict[ str, __.typx.Any ],
    results_max: int
) -> list[ dict[ str, __.typx.Any ] ]:
    ''' Selects top objects from inventory, sorted by fuzzy score. '''
    all_objects: list[ dict[ str, __.typx.Any ] ] = [ ]
    for domain_objects in inventory_data[ 'objects' ].values( ):
        all_objects.extend( domain_objects )
    all_objects.sort(
        key = lambda obj: obj.get( 'fuzzy_score', 0 ),
        reverse = True )
    return all_objects[ : results_max ]


def _validate_extraction_results(
    results: __.cabc.Sequence[ __.cabc.Mapping[ str, __.typx.Any ] ],
    requested_objects: __.cabc.Sequence[ __.cabc.Mapping[ str, __.typx.Any ] ],
    processor_name: str,
    source: str
) -> None:
    ''' Validates that extraction results contain meaningful content. '''
    if not requested_objects: return
    if not results:
        raise _exceptions.StructureIncompatibility( processor_name, source )
    meaningful_results = 0
    for result in results:
        signature = result.get( 'signature', '' ).strip( )
        description = result.get( 'description', '' ).strip( )
        if signature or description: meaningful_results += 1
    success_rate = meaningful_results / len( requested_objects )
    if success_rate < _SUCCESS_RATE_MINIMUM:
        raise _exceptions.ContentExtractFailure(
            processor_name, source, meaningful_results,
            len( requested_objects ) )
