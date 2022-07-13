# Dotnet DevSecOps tools

## Common

These tools are appropriate in all .NET repositories:

* [Directory.Build.props](common/Directory.Build.props)
* GitHub Actions
  * [Sample Build Workflow](common/sample-build-workflow.yml)
  * [Sample CodeQL Scanning Workflow](common/sample-codeql-workflow.yml)
  * [Sample Dependency Review Workflow](../common/sample-dependencies-workflow.ymik)

Also, for code quality checking, install the following NuGet packages in each
project:

```bash
dotnet add package Microsoft.CodeAnalysis
dotnet add package Microsoft.CodeAnalysis.CSharp.CodeStyle
dotnet add package SonarAnalyzer.CSharp
```

## Open Source

These tools are appropriate only in open source repositories.

* [.editorconfig](open/.editorconfig)

## Closed Source

These tools should be used in closed source repositories.

* [.editorconfig](closed/.editorconfig)
