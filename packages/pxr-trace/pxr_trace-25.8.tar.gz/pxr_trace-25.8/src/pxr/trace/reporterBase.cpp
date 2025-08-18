// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/trace/reporterBase.h"

#include "pxr/trace/pxr.h"
#include "pxr/trace/collector.h"
#include "pxr/trace/serialization.h"

TRACE_NAMESPACE_OPEN_SCOPE

TraceReporterBase::TraceReporterBase(DataSourcePtr dataSource)
    : _dataSource(std::move(dataSource))
{
}

bool TraceReporterBase::SerializeProcessedCollections(std::ostream& ostr) const
{
    std::vector<CollectionPtr> collections;
    for (const CollectionPtr& col : _processedCollections) {
        collections.push_back(col);
    }
    return TraceSerialization::Write(ostr, collections);
}

TraceReporterBase::~TraceReporterBase()
{
}

void
TraceReporterBase::_Clear()
{
    _processedCollections.clear();
    if (_dataSource) {
        _dataSource->Clear();
    }
}

void
TraceReporterBase::_Update()
{
    if (!_dataSource) return;

    std::vector<CollectionPtr> data = _dataSource->ConsumeData();
    for (const CollectionPtr& collection : data) {
        _ProcessCollection(collection);
        _processedCollections.push_back(collection);
    }
}

TRACE_NAMESPACE_CLOSE_SCOPE
