# Python API Archetype
# TODO
- Documentation
## Additional Features
- search movies
- logging
- jwt support
- testing


# Architecture
This archetype is structured roughly following a hexagonal (or ports and adapters) architecture, with protocols defining the ports and with implementatations of the protocols and routes forming the adapters. Routes depend on the protocols and rely on dependecy injection to provide the correct implementation. Data access is modeled by a repository pattern.

## Project Structure
- `app/api` is the REST API layer where routes are defined. Code here can depend on code in the domain and infrastructure folders, though ideally on abstractions.
    - the app.py file is where the API is initialized and acts as the entry point to the API
- `app/config` is where configuration lives
- `app/domain` is where the core business logic or "domain" is defined, as well as the definition of protocols. Code in this folder shouldn't directly depend on code in the api or infrastructure folders.
    - `/protocols` contains folders for each type of protocol (service, repository, etc) and inside are the protocols themselves
    - `/services` are the application services
    - `/models` represent the domain objects (e.g. Movies) and can contain business logic. They generally shouldn't have dependecies from other folders. In this example case, the models are light on business logic, though do include some validation. There is some mixing of database and domain models that in a more complex app could be separated.
- `app/infrastructure` contains all of the supporting code that the rest of the application relies upon. Implementations of ports lives here (e.g. specific implementations of the Movies repository, in this case a SQLite implementation)
# Development

In general, look for `# TODO` comments through the code to find places for custom development. Use the `movies.py` files as examples to replace with your required code.
## Routes
Each file in `app/api/routes` corresponds to a resource, with each file containing the individual methods available on each resource. The root route is reserved for special cases, such as the health check or an OAuth callback. Following the pattern, each route router should be registered in the `app/api/routes/__init__.py` file.

## Configuration
Config is handled via a Settings object. This `Settings` object is environment aware and will attempt to load values from environment variables. For local development, you can use python-dotenv and a `.env` file in the top-level folder to set values. Once deployed, the application can use the server environment variables or the `.env` file or both.

## Dependencies
Add new dependencies using `pip install`. Save the dependencies using `pip freeze > requirements.txt`. Make sure `requirements.txt` is version controlled.

# Deployment
Deployment occurs via a CI/CD pipeline in [Bamboo](build.ucsd.edu). The build step pulls dependencies and tests the code inside the target Docker container, and then packages the application into a Docker image published to Artifactory. The deployment step utilizes Helm and a Helm chart to deploy to EKS. Configuration of the Helm chart is available via the values.yaml file provided. The Helm chart has place to define environment variables and secrets, which can be filled in at deploy time from Bamboo.