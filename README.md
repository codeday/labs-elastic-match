# ElasticMatch
This project contains everything to run the CodeLabs automated elasticsearch matching system, including elasticsearch index definitions and a web API that is secured with JWT in order to securely and safely expose this functionality to the internet while still protecting the elasticsearch database itself. 

### Future work
Do you need to update the elasticsearch query? You're in for a real treat! I found that prototyping it in a Jupyter notebook is a good choice, since it allows you to quickly test many components of the query. Also, if you ever work with scripts, be sure to put the query execute into a try-except block, so you can get the very important information on script errors, otherwise you will be limited to a runtime or compile error. You can view all my work saved in the `old` folder.

### Folder Structure
There's a lot going on here, so let's quickly go over what's important and what isn't.
* `api` is where a lot of the good stuff is. This contains the elastic schema and queries that power student suggestions (look in the `elastic` folder) as well as the API that allows for the student (and soon mentor) preference UIs to get the data they need. 
* `data` is just a place for me to store pieces of data that need to be loaded or exported. This may or may not exist, depending on what Git does since it's contents are very likely all ignored.
* `old` is a place for old, no-longer-used scripts to go. I'm keeping them around, partly out of a sense of hoarding, but also because I need to keep adding stuff to this, and I'd like to keep the old stuff around just in case. 
* `setup` is code relevant to spinning up things. As of writing, it's just some imports stuff, but his might grow soon.
* `testing` is for thing related to, you guessed it, testing! I haven't written tests yet (hopefully that will happen soonish), but right now it contains things to make testing/dummy data for elastic and to test elastic and the API.

### A note on requirements
This project is pretty complex, and because of that, I have development and production requirements. requirements-api.txt is for the API in production 