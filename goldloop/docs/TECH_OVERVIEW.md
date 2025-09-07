# Technical Overview

Goldloop is composed of modular scripts that interact via a SQLite database and simple JSON files.

* **audience_ingest**: loads CSV audience data into the database.
* **persona_engine**: clusters the audience and generates fictional personas using GPT-4o.
* **content_generator**: produces blog content for a persona and topic.
* **ad_builder**: creates ad copy.
* **campaign_scheduler**: assigns publish times within a configurable window.
* **post_engine**: posts content to WordPress or sends via email.
* **monetizer**: generates PayPal checkout links.
* **analytics_logger**: records basic interaction events.
* **dashboard**: a small Flask application for viewing logs.
