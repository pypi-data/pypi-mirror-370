# parrygg-python

The official Python client library for the parry.gg tournament platform API. This library provides easy access to all parry.gg services using gRPC, allowing you to build applications that interact with tournaments, events, brackets, users, and more.

## Installation

```bash
pip install parrygg
```

## Requirements

- Python 3.7+
- grpcio
- grpcio-tools
- protobuf

## Usage

### Example

For authenticated requests, include your API key in the `X-API-KEY` header:

```python
import grpc
from parrygg.services.tournament_service_pb2_grpc import TournamentServiceStub
from parrygg.services.tournament_service_pb2 import GetTournamentsRequest

# Your API key from parry.gg
API_KEY = "your-api-key-here"

channel = grpc.secure_channel("api.parry.gg:443", grpc.ssl_channel_credentials())

tournament_service = TournamentServiceStub(channel)

metadata = [("x-api-key", API_KEY)]

request = GetTournamentsRequest()
response = tournament_service.GetTournaments(request, metadata=metadata)

print(f"Successfully retrieved {len(response.tournaments)} tournaments")
for tournament in response.tournaments:
    print(f"- {tournament.name} (ID: {tournament.id})")

channel.close()
```

## Available Services

The library provides access to all parry.gg API services:

- **TournamentService** - Tournament management and retrieval
- **EventService** - Event operations within tournaments
- **BracketService** - Bracket and match management
- **UserService** - User account operations
- **EntrantService** - Tournament participant management
- **PhaseService** - Tournament phase operations
- **GameService** - Game information and metadata
- **HierarchyService** - Organizational hierarchy management
- **NotificationService** - Notification operations
- **MatchService** - Individual match operations
- **PageContentService** - Content management

## Documentation

For comprehensive API documentation, authentication details, and developer resources, visit:

**[developer.parry.gg](https://developer.parry.gg)**

The developer portal includes:
- Complete API reference
- Authentication guide
- Code examples
- Rate limiting information
- Webhook documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For API support and questions, please visit [developer.parry.gg](https://developer.parry.gg) or contact the parry.gg development team.
