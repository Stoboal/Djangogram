## Djangogramm
Instagram-like study project

## Steps of deploying Django Project on GCP
General guide by Google: 
```
https://cloud.google.com/python/django
```
1. Create and write your Django project
2. Required ***Google Services***:
- App Engine
- Secret manager
- Google bucket
- Google Cloud SQL
- Required accesses between services
3. Prepare project ***settings*** to deploy:
- Create ***.env*** with: SECRET_KEY, DEBUG, ALLOWED_HOSTS, DB info, etc.
- Libraries: ***google.cloud***
- Config access to secret key hidden in ***Secret Manager***
- Add or config variables: ***MEDIA_URL***, ***DEFAULT_FILE_STORAGE***, ***GS_BUCKET_NAME***, ***GS_DEFAULT_ACL***, ***DATABASES***, ***ALLOWED_HOSTS***, ***INSTALLED_APPS***, ***DEBUG***, ***DATABASES***, etc
4. Write ***app.yaml***
5. Connect to ***Google Console*** and ***deploy***

## Setting up connection to SQL:
1. *To prevent connection issues kill ***postgresql*** process manually in Task Manager*
2. Download ***cloud-sql-proxy.exe***
3. Run it in separate terminal by using command ***'cloud-sql-proxy.exe PROJECT_ID:REGION:INSTANCE_NAME'***
4. Run in ***IDE*** terminal ***'echo $env:GOOGLE_CLOUD_PROJECT=project_ID'*** and get '=project_id' as response
5. Run in ***IDE*** terminal ***'echo $env:USE_CLOUD_SQL_AUTH_PROXY = "true"'*** and get 'true' as response
6. Make ***migrations***, then  ***migrate***


## Contributors

Bohdan Stoliarov

## License

This project is licensed under the MIT License - see the LICENSE file for details.
