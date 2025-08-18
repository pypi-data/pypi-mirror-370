# Connectors Directory

Place your healthcare API connector JSON files in this directory.

## Example Connector Configuration

Create a file like `my_healthcare_api.json`:

```json
{
  "name": "my_healthcare_api",
  "base_url": "https://api.healthcare-provider.com",
  "auth": {
    "type": "oauth2",
    "client_id_env": "MY_API_CLIENT_ID",
    "client_secret_env": "MY_API_CLIENT_SECRET",
    "token_url": "https://auth.healthcare-provider.com/oauth/token"
  },
  "endpoints": {
    "get_patient_data": {
      "method": "GET",
      "path": "/patients/{patient_id}",
      "description": "Retrieve patient information"
    },
    "search_codes": {
      "method": "GET", 
      "path": "/codes/search",
      "description": "Search medical codes",
      "query_params": {
        "code_type": "string",
        "search_term": "string"
      }
    }
  }
}
```

## Environment Variables

Add corresponding environment variables to your `.env` file:

```bash
ENABLE_MY_HEALTHCARE_API=true
MY_API_CLIENT_ID=your_client_id
MY_API_CLIENT_SECRET=your_client_secret
```

The connectors will be automatically discovered and loaded when the server starts.
