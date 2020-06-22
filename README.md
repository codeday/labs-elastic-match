# ElasticMatch
This project contains everything to run the CodeLabs automated elasticsearch matching system, including elasticsearch index definitions and a web API that is secured with JWT in order to securely and safely expose this functionality to the internet while still protecting the elasticsearch database itself. 

### Future work
Do you need to update the elasticsearch query? You're in for a real treat! I found that prototyping it in a Jupyter notebook is a good choice, since it allows you to quickly test many components of the query. Also, if you ever work with scripts, be sure to put the query execute into a try-except block so you can get the very very important information on script errors, otherwise you will be limited to a runtime or compile error. 