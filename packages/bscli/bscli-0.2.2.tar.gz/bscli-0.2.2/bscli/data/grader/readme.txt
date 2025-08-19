The use of the included scripts is entirely optional, but will likely save you a lot of time.
If you do not wish to use the scripts, just grade the submissions contained in it in a way that works for you.
All that matters is that you find a way to enter the grades in Brightspace, and get feedback to the students.
The scripts in here are mainly designed to be ran on a Linux machine, but the upload script should also work on Windows (TODO: untested at the moment).
Do note that the files generally have unix line endings, so please use a sane editor that supports them.

In a nutshell it works as follows:
- Every submission you have to grade has its own folder in the submissions/ folder.
- You grade the submission by filling out the feedback.txt template in each folder with a grade and feedback.
- Once all are graded you run an upload.py script to upload the grades and feedback to Brightspace using their API.

The grading_instructions.txt file describes the type of grade you have to enter in feedback.txt.
It is automatically generated each time a distribution is made and sent out.
So if you have to grade different assignments throughout a course with different kinds of grades, it may contain different information.

Some courses have more specialized needs, in which case a course_readme.txt should also exist with more course specific information.
Be sure it read it if that file also exists.
If not, this readme and the grading instructions should contain all the information needed to get up and running.



[1. One time setup]

To run the upload script and use the API wrapper you need a somewhat recent Python3 install (>=3.10).
The API wrapper can be installed using `python3 -m pip install brightspace-api`.

It is up to you to decide how to set up your environment.
Installing system wide is possible, but then keep in mind you may have to manage the dependencies if updates occur.

Using virtualenv is recommended, as the included upload-virtualenv.sh script will:
- Create a new temporary venv environment for you.
- Install the Brightspace API dependency.
- Run the upload.py script.
- Remove the temporary venv environment once done.

This means you can just run upload-virtualenv.sh once done grading and do not have to bother managing dependencies.
It does mean you have to have virtualenv installed, e.g. by executing `python3 -m pip install virtualenv`.
See instructions for your platform if this does not work.

You may also want to grade in a dedicated Virtual Machine.
Generally students are not outright hostile, but they may submit dodgy/broken stuff.
Always be -very- careful when running any student code/scripts, as they may damage your system.
Running in a VM mitigates this, and with snapshots you can easily restore if any unrecoverable damage occurs.
This is probably less of an issue with courses that mainly submit PDFs compared to code, but even then know you are taking risks if you run it directly on your own machine!


[1.1 Brightspace API]

To access the Brightspace API you need to authenticate yourself by logging in at a Brightspace login page.
This will generate a userId and userKey pair, where the userKey is used to sign data and thus should be kept secret!
This userId and userKey pair is called an "identity", and does not expire.
Remembering these identities allows us to avoid having to authenticate again and again by logging in each time we use the API.
For that reason the API wrapper includes a "manager" program to store and manage these identities on your system.
This makes it easy to switch between identities if you have multiple accounts, e.g. s-number/e-number/u-number.
It also means you only have to set up each identity once system-wide, and can re-use them for various courses.
Do note you should only store identities on trusted systems; do not store an identity on a public/shared machine as anyone can steal it then!
Essentially treat them as private keys.

When you run the upload script it will ask you to select an identity to use for the API access.
Initially you will not have any identities, so start the manager, and begin adding a new identity using the "auth" method.
This method will generate a URL you can open in your browser.
You should see the familiar Brightspace login page, so log in with your correct credentials.
After logging in it should (eventually) redirect you to a specific page/URL that contains your userId and userKey values as URL parameters.
Copy/paste this URL back into the manager to let it extract the identity, and complete adding the identity.

You should now have a working identity, so exit the manager to get back to the select screen.
Here you can now select the identity created to use with the upload script.
If you run the upload script again, even in future distributions, your created identity should still be there.

When you select an identity it will also ask you if you always want to use this identity for a specific "tag".
This tag is usually a course iteration specific value, such as "proc-2425" for Processors in the 2024-2025 iteration of the course.
Generally you use the same identity throughout a course iteration, so by marking it default for that tag you avoid the need to select that identity every time.
Instead, the upload script will check if an identity exists with that tag attached to it, and automatically use it.

It is also possible to start the manager by giving the upload script a '-m' or '--manage' flag, e.g. `python3 upload.py --manage`.
This may be useful if you mark an incorrect identity as default and want to clear it, as it is not possible to get to the manager via a select screen since it is skipped in that case.

To summarize the one time setup when first running the upload script:
- Create an identity for your Brightspace login credentials if need be.
- Select the identity that has access to the course.
- Mark it as default.

Now any future runs of the upload script for this course iteration will automatically select that identity without further interaction.



[2. Grading process]

This section explains the grading process you repeat every week.


[2.1 Some background information]

The material you need to grade is in the 'submissions/' folder.
There is a separate folder for each submission that needs to be graded.
The folder name of each submission depends on the type of assignment.
For individual assignments it will be named after the student number of the respective student.
For group assignments it will be named based on the group name.

Inside each submission folder are the following files and folders:

- feedback.txt
You modify this template with your feedback and grade.
It also contains some helpful meta data regarding that submission.
The exact contents are described below.

- grading_instructions.txt
A generated file that explains the type of grade you are expected to enter.

- course_readme.txt
Optional file that may be present if supplied by the course.

- submissions/
The folder containing the student submissions for you to grade.

- data/
The folder containing the upload script(s), dependencies, and some other data.

You may see additional files or folders.
This is because data can be "injected" at both the top-level (once per archive), and submission level (once per submission).
Typical top-level data is a reference solution, an assignment PDF, or some kind of grading notes.
Data injected for each submission may be files needed for tests, or other common files needed but not included by students.
All this is done on a per-course per-distribution basis however, so anything non-obvious should be explained in a course readme.

Archives (7z/tar/rar/zip) are generally automatically extracted and removed.
If this fails for whatever reason, the archive that failed to extract should still be there.
See if you can manually fix it, but usually this indicates a problem with a student submission such as corrupted files.

Depending on the exact course configuration some files and folders are automatically removed from student submissions after extracting archives.
Typically this includes stuff like ".git" folders, or unwanted file extensions such as ".exe".
If in doubt you can always download their submitted files manually from Brightspace if something is missing, but that is an exceptional situation that should not occur often.


[2.2 Feedback template]

The feedback.txt template looks something along the lines of:

Assignment: Assignment 1 - Boolean algebra
Submitted by: John Doe (s1234567)
Submitted at: 2024-11-06 14:52:48
Group: Group 7
Group member: John Doe (s1234567)
Group member: Bobby Tables (s7654321)
====================[Brightspace comment]====================
The comment provided when submitting in Brightspace, if any
====================[Enter grade below]======================
TODO
====================[Enter feedback below]===================


The "Assignment" field denotes the name of the assignment in Brightspace.

The "Submitted by" field denotes the student who made the submission.

The "Submitted at" field denotes the time of the submission.
Note that this time is not UTC, but in the local timezone of the distribution scripts.
Typically this means the time should match that of the local NL time.
If it is possible to submit after a due date, you may see any late submissions marked as such.
This is done via a "(!!!LATE!!! N day(s), 01h:23m:45s)" string behind the date, indicating how long past the due date the submission was.
How to handle such late submissions, if even possible, is course-specific, so defer to instructions you received if relevant.

The "Group" field denotes the name of the Brightspace group who made the submission.
This field is only shown for group assignments.

The "Group member" fields denote all members of the Brightspace group who made the submission.
These fields are only shown for group assignments.
Note that it shows the group members at the time of distribution, and not at the time of submission.
This is a Brightspace limitation; if students leave groups before distributions are made we have no way of seeing this.

The field between the "Brightspace comment" and "Enter grade below" headers denotes the Brightspace submission comment.
Usually students leave this empty, but every now and then it does contain relevant information, so make sure to quickly skim it if one was given.

All these fields so far are just meta data; look at it to get relevant information if need be, but you do not do anything with it.
The next two fields are what you have to fill in.

The field between the "Enter grade below" and "Enter feedback below" is parsed by the upload script to determine the grade for this submission.
By default it contains the "TODO" placeholder to indicate the submission has not yet been graded.
See grading_instructions.txt for the specific grade values expected.

The rest of the file, after the "Enter feedback below" header is considered the feedback for this submission.
See the next section for more information regarding this feedback field.


[2.3 Entering the feedback]

The text you enter is mostly in plain text.
While Brightspace technically support plain text feedback, it mangles formatting to a large degree.
This makes it very hard to use effectively, especially for programming (related) courses that want to give code feedback.
As such, the feedback text you provide is processed and converted to the more typical HTML rich text feedback Brightspace uses.
This allows use to specify inline code, and even full code blocks with syntax highlighting and line numbers.

Doing so via the web interface is very tedious, but in the feedback template you should hopefully find it very easy, and similar to Markdown.

[2.3.1 Paragraphs]

Before we get into that, you must first be aware of how paragraphs are formed from your feedback.
Basically lines are joined together into HTML paragraphs, unless separated by a blank line, similar to Markdown.

Some examples:

---------------------------------------
This is an example.
Still part of the same paragraph.

This will form a new paragraph however.

You can even
break up sentences over
multiple lines, no
problem at all! This may
be useful to avoid line wrapping
in your editor.


Multiple blank lines will cause an
empty paragraph for even more
vertical spacing.
---------------------------------------

produces

---------------------------------------
<p>This is an example. Still part of the same paragraph.</p>
<p>This will form a new paragraph however.</p>
<p>You can even break up sentences over multiple lines, no problem at all! This may be useful to avoid line wrapping in your editor.</p>
<p></p>
<p>Multiple blank lines will cause an empty paragraph for even more vertical spacing.</p>
---------------------------------------

Do not overuse empty paragraphs; there is already quite a bit of vertical spacing between paragraphs.

[2.3.2 Inline code]

Any text -on the same line- that is placed between single back-tick characters (`) is styled as a <code> tag.
This will render that text in a mono-spaced font with a slightly different background color.
While not suited for larger snippets of code, especially because it -cannot- span over multiple lines, it is ideal to style e.g. references to function names.
It also does not apply any syntax highlighting.

Some examples:

---------------------------------------
You can call `infile.is_open()` to check if the input file stream `infile` is opened.
---------------------------------------

produces

---------------------------------------
You can call <code>infile.is_open()</code> to check if the input file stream <code>infile</code> is opened.
---------------------------------------

The feedback text is HTML escaped before applying such code tags.
This means you can safely place HTML tags in your feedback, but due to the escaping they will not be rendered as HTML tags.
For example "<b>test</b>" will not cause your "test" to show as bold.
Instead it will just show the text "<b>test</b>" in the Brightspace feedback.

[2.3.3 Code blocks]

By placing text between triple back-tick characters (```) you can create actual code blocks in the HTML feedback.
These code blocks have basic syntax highlighting, line number information, and a configurable language.
This language is shown in the top-right of the code block, and can be used to indicate which programming language a code block contains.

If you do not specify a programming language, a default one is used instead.
The default depends on the course, and is mentioned in the grading_instructions.txt file.

There are several ways to use code blocks, as shown in these examples:

---------------------------------------
The most basic example, using the default language.

```
int a = 0;
int b = 1;
int c = a + b;
```

Another example: ```
a = [1, 2, 3]
b = []
c.extend(a)``` Feedback text continues here,
but will be shown in a different paragraph.

Specify the language as java:
```java
public static void main(String[] args) {
  System.out.println("Hello, world!");
}
```
---------------------------------------

produces

---------------------------------------
<p>The most basic example, using the default language.</p>
<pre class="d2l-code line-numbers"><code class="language-clike">
int a = 0;
int b = 1;
int c = a + b;
</code></pre>
<p>Another example:</p>
<pre class="d2l-code line-numbers"><code class="language-clike">
a = [1, 2, 3]
b = []
c.extend(a)
</code></pre>
<p>Feedback text continues here, but will be shown in a different paragraph.</p>
<pre class="d2l-code line-numbers"><code class="language-java">
public static void main(String[] args) {
  System.out.println("Hello, world!");
}
</code></pre>
---------------------------------------

This assumes the default language is 'clike'.
Note that the exact HTML produced by the upload script may be slightly different.
Like with inline code, HTML escaping is applied prior to constructing these code blocks so HTML tags in your code snippets do not cause issues.

There are some things to watch out for when specifying code blocks.
The text after the opening ``` until the next line is considered the language specifier.
This language specifier -must- be one of the available languages specified below.
Be careful not to put code on the same line after the opening ```.
Doing so will cause that code to be interpreted as the language specifier.

Some examples of BAD code blocks:

---------------------------------------
Bad language: ```zig
pub fn main() void {
  // ...
}```

Code as language: ```int a = 0;
int b = a + 2;
```

Not closing block: ```
cout << "oops";
I forgot to close the block!
---------------------------------------

The first example is bad because 'zig' is not an available language specifier.

The second example is bad because it sees 'int a = 0;' as the language specifier, which is not valid.

The third example is bad because the block is never closed with ```.

In the first and second example, the upload script should produce a warning, and it will consider the language specifier as code.
In the second example this fixes the problem (do not rely on this!), but in the first example we are left with an unwanted 'zig' line as the first line of code.
In the third example it will ignore runaway code blocks like this, essentially acting as if the opening ``` does not exist.
This does mean the code will show up as normally (i.e. poorly) formatted text.
It should again produce a warning, so you may want to fix it and upload a corrected version.

Available languages: 'cpp', 'csharp', 'markup', 'java', 'javascript', 'python', 'arduino', 'armasm', 'bash', 'c', 'clike', 
                     'css', 'haskell', 'json', 'kotlin', 'latex', 'matlab', 'plain', 'r', 'racket', 'regex', 'sql', 'wolfram'

[2.3.4 Graded by suffix]

Since there is no direct way for students to see who graded their work, the upload script automatically attaches a suffix to your feedback.
This suffix states a student was graded by you, and that they can contact you on your @ru.nl email address.
Note this suffix is only added to the feedback sent to the API; the actual feedback.txt file is untouched.

If for whatever reason you prefer students contacting you on another email, then this can be configured on the distribution side.
Poke me and ask me to change it if you want this to happen.
Generally you should try to stick to university emails over (commercial) third parties, but perhaps there is some mess with account migrations or something for you.


[2.4 Attaching feedback files]

It is also possible to add files as attachments to the feedback shown to students.
One use case could be annotating PDFs submitted by students, and then attaching the annotated version to the feedback.
To attach such files, create an "__attach_feedback/" folder in each desired 'submissions/*/' folder (i.e. the one containing feedback.txt), and place any files to attach in there.
The upload script will then look for the existence of such folders, and attach any files found inside to the feedback of that submission.

Brightspace may reject large files (>500MiB), or files with some extensions (typically executable ones like .exe or .sh).
Normally that should not be an issue, but know some limitations exist.

It may not be obvious to students that there are extra feedback files attached, so probably best to mention it in the regular text feedback you provide.



[3. Upload process]

Once you finish grading all the submissions, you need to run the 'upload.py' Python3 script.
You can run this manually (e.g. 'python3 data/scripts/export.py' from a command line).
Preferably you use the 'upload-virtualenv.sh' wrapper to do this for you in a temporary virtual environment.

Please make sure you read all the output from this script, as it will warn you in case any errors were detected.
It is also an interactive script, so you have to provide some user input.
Running this script will create the files  'export/ASSIGNMENT-feedback.zip' and 'export/ASSIGNMENT-grades.csv' for you.
You should probably back these up during the course, as we can use them to fix stuff with minimal effort in case the API integration/Brightspace goes tits up.
Generally you can ignored them though; just dump them somewhere you can find them again, and feel free to delete them once a course is done.

You can technically import this grades CSV from the Brightspace grades book to set grades, but you should not do so unless you have good reasons.
This will set grades directly in the grade book, and not the assignment itself, and do nothing with feedback.
Using the API it will set grades and feedback on the assignment, which is then also applied on the linked grade.

When running the export script, you are asked if you want to upload the grades and feedback to Brightspace using the API.
You should probably select yes here, as doing this manually will probably take you quite some time.

In case everything goes smoothly, the feedback and grades should be uploaded to Brightspace within seconds without problems, after which you're done grading the assignment.
In case you tried to override feedback/grades the script will provide you with some 'conflict resolution' methods.
This is an interactive process that asks you to make a decision on what feedback and grade to present to the students.

If the division of submissions was done correctly, this should not occur.
If you ran the script and only partially uploaded feedback, as some of your submissions contained errors (e.g. invalid grade due to a typo), then this also allows you to simply rerun the script after fixing errors.
When prompted pick the option to discard feedback you already uploaded successfully.
In any case, existing feedback is backed up to the export directory in the raw HTML form, so it should be hard to really screw things up.
You can always copy/paste this HTML back in the editor in Brightspace, but do note that it only keeps a copy of the most recent feedback.
If you overwrite it multiple times, it will not keep a complete history.



[4. Extra stuff]

I personally grade on a Linux machine using bash/vim.
The 'bash-grading.sh' script contains some useful functions to ease this process.
This is entirely optional and not recommended unless you know what you are doing when it comes to Linux stuff, in which case you probably want to modify it anyway.

You can load it by opening a bash terminal in the folder that contains the 'submissions/' and 'data/' folders, followed by typing '. data/bash-grading.sh'.
You can then run the command 'startgrading' to begin grading.
You will be moved to the first submission, where a "grading function" is executed.
This grading function typically does stuff like open all PDF files in my viewer, open plain text files in vim, open the feedback.txt file, etc.
Once you finish grading a submission, run 'next' to move to the next submission, once again executing the grading function.
It will print 'Finished grading' if all submissions have been graded.
You can then run 'finishgrading' to execute the upload script.

This script basically automates executing a bunch of repetitive commands to boost productivity, but is entirely built around my work flow.
You should probably look at the script and understand what it does before attempting to use it.
Feel free to make your own changes to match your work flow if desired.
Note that some courses might have a custom grading function (course_grading_function.sh).
In those cases that file contains the main grading automation, whereas the regular bash-grading.sh serves mostly as a way to move between submissions.
