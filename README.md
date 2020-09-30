# Django PMS(Project Management System)
<p><b>Project Management System(PMS)</b> is a simple hobby project created in Django v3.1.1. It uses simple css along with Bootstrap 4 framework. For database part, I have used default sqlite3.</p>
<p>About 50% of the projects operation is done with the default admin site and rest with custom site.</p>

<p> Mainly there are two types of users:</p>
<ol>
<li>superuser</li>
<li>user</li>
<ol>
<li>Project Leader</li>
<li>Project Member</li>
</ol>
</ol>

<p>Operations</p>
<ol>
<li>
superuser
<ul>

<li>creates new user</li>
<li>creates new project</li>
<li>creates roles e.g. project leader, project memeber</li>
<li>creates status for story/service request e.g. new, inprogress, testing, completed etc</li>
<li>assgins user to project along with roles</li>
<b>Note : </b>All above operations are done through admin site.

</ul>
</li>
<li>
user
<ol>
<li>
 project leader
 <ul>
 <li style="list-style-type:circle">create and update story/service request(sr)</li>
 <li style="list-style-type:circle">assign status to the sr</li>
 <li style="list-style-type:circle">assign user to the created story</li>
 <li style="list-style-type:circle">view all associated project</li>
 <li style="list-style-type:circle">view status of each project</li>
 
 </ul>
</li>
<li>
 project member
 <ul>
 <li style="list-style-type:circle">can view all associated projects</li>
 <li style="list-style-type:circle">view status of each project</li>
 <li style="list-style-type:circle">view status of each sr</li>
 <li style="list-style-type:circle">change status of each sr/story</li>
 
 </ul>
</li>
</ol>
</li>
</ol>
