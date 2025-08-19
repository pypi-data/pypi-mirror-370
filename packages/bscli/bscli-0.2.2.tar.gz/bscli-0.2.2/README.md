# Brightspace Command Line Interface (`bscli`)

`bscli` is a command line interface for D2L Brightspace LMS that simplifies and automates assignment grading workflows.
It provides the ability to download assignment submissions via the command line (which is fast) instead of using the web interface (which is slow).
`bscli` is designed for educational institutions and can be adapted to work with any Brightspace instance.

Additionally, `bscli` is able to (semi-)automate grading and distribution of homework assignments.
It can download submissions, process them automatically, and distribute them to graders.
These graders can then grade the assignments and upload their grades back to Brightspace.

You can use `bscli` in two ways: either by specifying course and assignment IDs manually for quick access, or by creating a dedicated folder for each course with a `course.json` file containing course-specific settings and aliases for assignments (recommended). 

Graders will receive an archive containing all submissions they were assigned to grade, and can write their feedback in a `feedback.txt` file (with partial Markdown support).
They can do so on their local machine, using any tools they prefer, without the need to interact with the Brightspace LMS web interface.
Once they are done, they can upload their feedback via the Brightspace API.

More specifically, submissions are downloaded, and after potential preprocessing, an `.7z` archive is created for each grader containing the submissions they are assigned to grade.
There are several strategies to distribute submissions to graders, such as randomly or according to Brightspace group registration.
The archives can be sent to graders via FileSender.

The automated processing pipeline works as follows:
1. **Download** submissions from Brightspace
2. **Preprocess** submissions (remove unwanted files, convert formats, organize structure)
3. **Distribute** submissions to graders using the configured strategy
4. **Package** submissions into encrypted `.7z` archives for each grader
5. **Deliver** archives to graders via FileSender with password protection
6. **Upload** graded feedback back to Brightspace
Apart from Brightspace access, the scripts thus require access to a FileSender server.

Notice that files will be encrypted with a password while being uploaded to FileSender.
The password can be set per assignment, and must be provided to graders separately.
FileSender may not receive the password, and does not accept it being included in the email (they actively check for this).

## Installation

To install `bscli`, you need to have Python 3.10 or higher installed on your system.
You can install `bscli` using `pip`:

```bash
pip install bscli
```

If you want to use `bscli` for automatically processing homework assignments, you also need to install some additional OS packages:
- `7za` - to create the encrypted archives
- `libreoffice` - to convert .docx files to .pdf files (optional)

## Configuration

Before you can use `bscli`, you need to configure it with your Brightspace instance and FileSender credentials.

### Brightspace configuration
To use `bscli`, you need to configure it with API credentials specific to your Brightspace instance.
You should receive these credentials from your Brightspace administrator.
You can configure `bscli` by running the following command:

```bash
bscli config init bsapi
```

This will prompt you for the necessary credentials and save them in a configuration file on your system (by default in `~/.config/bscli/bsapi.json`).

### FileSender configuration
If you want to use `bscli` for distributing homework assignments to graders, you also need to configure FileSender credentials.
FileSender is a service that allows you to send large files securely and `bscli` is able to upload files to FileSender directly.
To configure FileSender, you need to have an account on a FileSender service and obtain the API credentials.
You can configure `bscli` for FileSender by running the following command:

```bash
bscli config init filesender
```

This will prompt you for the necessary credentials and save them in a configuration file (by default in `~/.config/bscli/filesender.json`).

You can use the SURF FileSender instance and acquire the credentials via https://filesender.surf.nl/?s=user.
You need a `username` (which can be a random string), `email address`, and `api key` (also a long random string).

### Authentication
Most commands in `bscli` require authentication to access Brightspace on your behalf.
`bscli` will prompt you to authenticate when you run a command that requires it.
You can also authenticate manually by running the following command:

```bash
bscli config authorize
```

This will open a web browser where you can log in to Brightspace and authorize `bscli` to access your account.
If you have already authenticated, `bscli` will use the existing authentication token as long as it is valid. 
This is typically a few hours, depending on your Brightspace instance configuration (this is not controlled by `bscli`). 

## Basic usage

`bscli` is an actual command line interface with subcommands, similar to `git` or `docker`.
For a list of available commands, you can run:

```bash
bscli --help
```

For example, to list all courses you have access to, you can run:

```bash
bscli courses list
```

To list all assignments in a specific course, you can run:

```bash
bscli assignments list --course-id <course_id>
```

or if you have a `course.json` file in your current directory (see below), you can simply run:

```bash
bscli assignments list
```

Then, to download all submissions for a specific assignment, you can run:

```bash
bscli submissions download --course-id <course_id> --assignment-id <assignment_id>
```

or if you have a `course.json` file in your current directory specifying the alias `A01` for a specific assignment, you can run:

```bash
bscli submissions download A01
```

### Two usage modes

**Direct mode (quick access):**
For quick operations, you can specify course and assignment IDs directly:
```bash
bscli assignments list --course-id 12345
bscli assignments download --course-id 12345 --assignment-id 67890
bscli assignments grading-progress --course-id 12345 --assignment-id 67890
```

**Course configuration mode (recommended):**
For regular use, create a dedicated folder for each course and configure a `course.json` file.
This allows you to use assignment aliases and enables advanced grading automation features.
You can create a default configuration file by running `bscli courses config-create`.
Typically, you create this file once per course, and then modify it as needed.

```bash
mkdir my-course-2025
cd my-course-2025
bscli courses config-create
bscli assignments download homework-1    # Uses alias from course.json
bscli assignments distribute homework-1  # Automated distribution with custom processing
```

### Course configuration
Most commands are related to a specific Brightspace course.
Though you can specify the course ID explicitly using the `--course-id` option, it is often more convenient to create a `course.json` file in your current directory (containing anything related for a specific course, such as aliases for assignments).
By default, `bscli` will look for a `course.json` file in the current directory and use it for all commands.
In this `course.json` file, you can specify the course ID and other course-specific grading settings for distributing assignments.
Typically, one grader coordinator creates this file for a course and shares it with whoever needs it.

You can create a `course.json` file by running:

```bash
bscli courses config-create
```

This will prompt you for all kinds of course-specific settings and aliases and save them in a `course.json` file.
You can also edit the file manually.

### Distributing assignments
If you want to distribute assignments to graders, you can use the `bscli distribute` command.
This command will:

1. download all submissions for the specific assignment
2. process them automatically (e.g., unzip archives, convert .docx files to .pdf files, remove specific files, inject specific files, etc.)
3. divide the submissions into groups for each grader according to the course configuration
4. upload the groups to FileSender and send the links to the graders via email

Notice that for privacy, the submissions should be encrypted with a password before uploading to FileSender.
This password can be set in the course configuration file (`course.json`) for each assignment.
Graders will need to input this password to download the submissions from FileSender.
This password is not sent via email to the graders (SURF does not allow it), so it needs to be communicated separately (e.g. in person).

If you do not set a password, `bscli` will not encrypt the submissions and will upload them directly to FileSender.
Notice that this is not recommended!

### Uploading feedback and grades
If you want to upload feedback and grades back to Brightspace, you can use the `bscli feedback upload` command.
This command will look for a `feedback.txt` file in the current directory, parse its contents and upload the feedback and grades to Brightspace.
A template `feedback.txt` file will automatically be created when you run the `bscli distribute` command.

## Advanced Configuration

`bscli` uses configuration files to store settings and credentials. 
The `bsapi.json` and `filesender.json` files are used to configure the Brightspace API and FileSender server respectively and are stored by default in the `~/.config/bscli/` directory.
More information on the contents of these files can be found below, or in the `/bscli/data/scheme/` directory that contains JSON schema files for these configuration files.

### `bsapi.json`
This file configures communication with the Brightspace API.
An example of the `bsapi.json` file can be found below. 

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "lmsUrl": "brightspace.example.com",
  "redirectUri": "https://redirect.example.com/callback",
  "leVersion": "1.79",
  "lpVersion": "1.47"
}
```

The settings should match those of a registered API application in your Brightspace LMS.

### OAuth Callback Setup

The `redirectUri` in your `bsapi.json` configuration must point to a publicly accessible HTTPS URL hosting the `callback.html` file. This is required because:

1. **Brightspace requires HTTPS**: OAuth redirects must use HTTPS for security
2. **CLI limitation**: The CLI runs locally and cannot directly receive HTTPS callbacks
3. **Bridge solution**: The callback page acts as a bridge between the HTTPS OAuth flow and your local CLI

#### Setting up the callback page

1. **Host the callback page**: Upload the `callback.html` file (included in this repository) to any web server with HTTPS support:
   - GitLab Pages (this repository includes GitLab CI configuration)
   - GitHub Pages
   - Your university's web hosting
   - Any cloud hosting service (Netlify, Vercel, etc.)

2. **Configure the redirect URI**: Set the `redirectUri` in your `bsapi.json` to point to your hosted callback page:
   ```json
   {
     "redirectUri": "https://yourdomain.gitlab.io/bsscripts/callback.html"
   }
   ```

3. **Register in Brightspace**: When registering your OAuth application in Brightspace, use the same HTTPS URL as your redirect URI.

#### How the OAuth flow works

1. CLI opens your browser to the Brightspace authorization URL
2. After authorization, Brightspace redirects to your hosted `callback.html` page
3. The callback page extracts the authorization code and either:
   - Automatically redirects to your local CLI (if supported)
   - Displays the code for manual copy-paste into the CLI
4. You enter the code in the CLI to complete authentication

#### Using GitLab Pages (Recommended)

This repository includes GitLab CI configuration (`.gitlab-ci.yml`) that automatically deploys the callback page to GitLab Pages:

1. **Fork or clone** this repository to your GitLab account
2. **Push to the main branch** - GitLab CI will automatically build and deploy the callback page
3. **Access your callback page** at `https://yourusername.gitlab.io/bsscripts/callback.html`
4. **Use this URL** as your `redirectUri` in `bsapi.json`

The GitLab CI configuration automatically copies `callback.html` to the `public` directory and deploys it to GitLab Pages on every push to the main branch.

### `course.json`
This file configures how the application should behave for a specific course.
It contains course-specific settings, such as the course ID, aliases for assignments, grading settings, et cetera.

```json
{
  "courseName": "Sandbox Course 2025", // name of the course in Brightspace
  "course": "sandbox", // internal alias for the course
  "assignmentDefaults": { // default grading settings for assignments
    "ignoredSubmissions": [], // submission ids to ignore
    "draftFeedback": false, // whether to upload feedback as draft or publish it immediately
    "defaultCodeBlockLanguage": "java", // default language for code blocks in feedback
    "fileHierarchy": "smart", // whether to keep the `original` submission's file hierarchy, `flatten`, or unpack in a `smart` way
    "division": { // how to divide the feedback archive
      // ... see below
    },
    "gradeAliases": { // aliases for grades, used in feedback
      "f": "Fail", // entering "f" as grade will be replaced by "Fail" in the feedback
      "i": "Insufficient",
      "s": "Sufficient",
      "g": "Good"
    },
    "removeFiles": [ // files to remove from submissions
      ".*",
      "*.exe",
      "*.jar",
      "*.a",
      "*.o",
      "*.class",
      "*.obj"
    ],
    "removeFolders": [ // folders to remove from submissions
      "__MACOSX",
      "__pycache__",
      ".*"
    ]
  },
  "assignments": { // assignments that should be graded
    "a1": { // 'a1' is the alias for this assignment which can be used in the scripts
      "name": "test assignment", // the name of the assignment in Brightspace
      "encryptionPassword": "MySecureP@ssword123" // the password to encrypt the feedback archive for this assignment, must contain at least one uppercase letter, one lowercase letter, one digit and one special character
    } // this can also contain the same settings as `assignmentDefaults` to override them for a specific assignment
  },
  "graders": { // who are the graders for this course
    "grader1": { // 'grader1' is the alias for this grader which can be used in the scripts
      "name": "Grader 1", // the display name of the grader
      "email": "grader1@example.com", // the email address that should receive the feedback archive
      "contactEmail": "grader1@example.com" // the email of the grader that will be used in the feedback to 
    }
  }
}
```

## Division strategies
There are several strategies to divide submissions to graders.
- `random`: submissions are divided randomly to graders
- `brightspace`: submissions are divided according to Brightspace groups (depending on which group the submitter is in, it will be divided to the corresponding grader)
- `persistent`: submissions are divided according to a persistent mapping of students to graders
- `custom`: a custom division strategy can be implemented as a `CourseModule`

### Random division
The random division strategy is the simplest division strategy.
Everytime you distribute submissions, they are randomly assigned to graders as specified in the `graders` field.
You should configure the following settings in the `course.json` file to use this strategy:
```json
{
  "division": {
    "method": "random",
    "graderWeights": {
      "grader1": 1,
      "grader2": 2
    }
  }
}
```

### Brightspace division
The Brightspace division strategy divides submissions according to Brightspace groups.
You should configure the following settings in the `course.json` file to use this strategy:
```json
{
  "division": {
    "method": "brightspace",
    "groupCategoryName": "Grading Groups",
    "groupMapping": {
      "Grading Group 1": "grader1",
      "Grading Group 2": "grader2"
    }
  }
}
```

### Persistent division
Make a random division once and store it in a file, so that the same division can be used in the future.
```json
{
  "division": {
    "method": "persistent", 
    "groupCategoryName": "grading-groups",
    "graderWeights": {
      "grader1": 1, 
      "grader2": 2
    }
  }
}
```

### Custom division
You can implement your own division strategy by creating a Python script as a `CourseModule`.
Place the script in `./data/course/<course>/plugin.py`.

