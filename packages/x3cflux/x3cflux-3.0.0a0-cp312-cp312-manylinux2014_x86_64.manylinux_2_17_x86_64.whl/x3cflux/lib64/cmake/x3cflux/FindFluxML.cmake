include(FindPackageHandleStandardArgs)

set(FLUXML_SEARCH_PATHS
        /usr
        /usr/local
        $ENV{FLUXML_PATH}
        )

find_package(XercesC REQUIRED)

find_path(FluxML_INCLUDE_DIR FluxML.h
        PATH_SUFFIXES include/fluxml
        PATHS ${FLUXML_SEARCH_PATHS}
        )

if (BUILD_SHARED_LIBS)
        set(fluxml_name FluxML)
else ()
        set(fluxml_name libFluxML.a)
endif ()
find_library(FluxML_LIBRARY_TMP
        NAMES ${fluxml_name}
        PATH_SUFFIXES lib
        PATHS ${FLUXML_SEARCH_PATHS}
        )

set(FluxML_LIBRARY ${XercesC_LIBRARIES} ${FluxML_LIBRARY_TMP})
find_package_handle_standard_args(FluxML REQUIRED_VARS FluxML_LIBRARY FluxML_INCLUDE_DIR XercesC_LIBRARIES)
