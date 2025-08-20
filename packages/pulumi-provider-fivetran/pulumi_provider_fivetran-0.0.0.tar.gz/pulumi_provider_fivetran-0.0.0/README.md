# Fivetran Pulumi Provider

The Fivetran Resource Provider lets you manage [Fivetran](https://www.fivetran.com) resources via it's RestAPI

## Installing

This package is available for several languages/platforms:

### Node.js (JavaScript/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

```bash
npm install @ryan-pip/pulumi-fivetran
```

or `yarn`:

```bash
yarn add @ryan-pip/pulumi-fivetran
```

### Python

To use from Python, install using `pip`:

```bash
pip install pulumi_provider_fivetran
```

### Go

To use from Go, use `go get` to grab the latest version of the library:

```bash
go get github.com/pulumi/pulumi-fivetran/sdk/go/...
```

### .NET

To use from .NET, install using `dotnet add package`:

```bash
dotnet add package Pulumi.Fivetran
```

## Configuration

The following configuration points are available for the `fivetran` provider:

- `fivetran:api_key` (environment: `FIVETRAN_API_KEY`) - the API key for `fivetran`
- `fivetran:api_secret` (environment: `FIVETRAN_API_SECRET`) - the API secret for `fivetran`

## Reference

For detailed reference documentation, please visit [the Pulumi registry](https://www.pulumi.com/registry/packages/foo/api-docs/).
