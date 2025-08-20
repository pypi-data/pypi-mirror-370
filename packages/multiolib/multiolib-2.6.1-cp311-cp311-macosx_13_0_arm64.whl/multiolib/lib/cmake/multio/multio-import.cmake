##################################################################
## Project features

set( multio_HAVE_FDB5      1    )
set( multio_HAVE_MAESTRO   0 )
set( multio_HAVE_MIR       1     )

##################################################################
## Project dependencies

include( CMakeFindDependencyMacro )

find_dependency( eccodes HINTS ${CMAKE_CURRENT_LIST_DIR}/../eccodes /tmp/multio/prereqs/eccodeslib/lib/cmake/eccodes )
find_dependency( eckit   HINTS ${CMAKE_CURRENT_LIST_DIR}/../eckit   /tmp/multio/prereqs/eckitlib/lib/cmake/eckit )
find_dependency( metkit  HINTS ${CMAKE_CURRENT_LIST_DIR}/../metkit  /tmp/multio/prereqs/metkitlib/lib/cmake/metkit )
find_dependency( atlas   HINTS ${CMAKE_CURRENT_LIST_DIR}/../atlas   /tmp/multio/prereqs/atlaslib-ecmwf/lib/cmake/atlas )

if( multio_HAVE_FDB5 )
  find_dependency( fdb5 HINTS ${CMAKE_CURRENT_LIST_DIR}/../fdb5 /tmp/multio/prereqs/fdb5lib/lib/cmake/fdb5 )
endif()

if( multio_HAVE_MIR )
  find_dependency( mir HINTS ${CMAKE_CURRENT_LIST_DIR}/../action/interpolate /tmp/multio/prereqs/mirlib/lib/cmake/mir )
endif()

if( multio_HAVE_MAESTRO )
  find_dependency( Maestro HINTS ${CMAKE_CURRENT_LIST_DIR}/../maestro  )
endif()
