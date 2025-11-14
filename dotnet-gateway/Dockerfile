FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Restore
COPY src/Gateway.Api/Gateway.Api.csproj ./Gateway.Api.csproj
RUN dotnet restore Gateway.Api.csproj

# Build and publish
COPY src/Gateway.Api/ ./ 
RUN dotnet publish Gateway.Api.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "Gateway.Api.dll"]

