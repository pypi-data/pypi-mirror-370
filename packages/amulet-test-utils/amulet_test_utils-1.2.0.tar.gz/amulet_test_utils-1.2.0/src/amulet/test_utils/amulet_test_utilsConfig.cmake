if (NOT TARGET amulet_test_utils)
    set(amulet_test_utils_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")

    add_library(amulet_test_utils INTERFACE)
    target_include_directories(amulet_test_utils INTERFACE ${amulet_test_utils_INCLUDE_DIR})
endif()
