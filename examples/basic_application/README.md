Basic example on how to use composer <br/>
Run the following: <br/>
`composer install -i a-test-app` <br/>
Get the application name with (has been manually set to 'a-test-app': <br/>
`composer list` <br/>
Get the logs for that application <br/>
`composer logs a-test-app` <br/>
You should see:
```bash
> composer logs a-test-app
Logs for: test-application
Attaching to example_container
example_container | Hello, World.
```
<br/>
Then uninstall the application: <br/>
`composer delete a-test-app` <br/>
Re-run with different values: (Note that order matters of the overrides) <br/>
`composer install -i a-test-app -v values.yaml -v override.yaml` <br/>
View the logs again, you should see a different message <br/>

```bash
> composer logs a-test-app
Logs for: test-application
Attaching to example_container
example_container | Hello again, with a different message.
```
<br/>
Jinja is a very powerful templating language, you can easily add different services based on values.yaml or deploy different images into different environments etc.