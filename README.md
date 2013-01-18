gen-compilation-db
==================

About
-----
Tools using clang want a compilation database to know what flags go with what
source files. See http://clang.llvm.org/docs/JSONCompilationDatabase.html.

This is a tool for generating and updating such a database from Xcode projects.

Usage
-----
    intercept-xcodebuild.py <output-db> <compiler-path> [xcodebuild args]
