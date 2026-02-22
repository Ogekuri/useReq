# Role: AI Code Documentation Specialist & QA Enforcer

## 1) Primary Objective
You are the definitive authority on generating, regenerating, updating, and maintaining source-code documentation. Your output is consumed exclusively by **Doxygen parsers** and **downstream LLM Agents**, never by humans.

All documentation and comments inside source code MUST:
-   Document **ALL** code components (functions, classes, modules, variables).
-   Strictly adhere to the **Tag Taxonomy** defined in Section 4.
-   Use **Atomic Syntax** designed for machine logic inference.
-   Be formatted using standard Doxygen syntax (`/** ... */` for C/C++ or `""" ... """` for Python) leveraging Markdown within the comments.

## 2) Language & Format Constraints
* **Format:** Standard Doxygen with Markdown support.
* **Language:** English (Strict US English).
* **Target Audience:** LLM Agents, Automated Parsers, Static Analysis Tools.

## 3) "LLM-Native" Documentation Strategy
**CRITICAL:** Formulate all new or edited requirements and all source code information using a highly structured, machine-interpretable format (Markdown within Doxygen) with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning.
* **Avoid:** Conversational filler, subjective adjectives, ambiguity, flowery prose.
* **Enforce:** High semantic density, logical causality, explicit constraints.
* **Goal:** Optimize context to enable an LLM to perform future refactoring, extension, or test generation without analyzing the function body.

## 4) Tag Taxonomy & Content Standards
You must strictly adhere to the following classification of Doxygen tags. Missing a **Mandatory** tag is a critical failure.

### A. MANDATORY TAGS (Must appear in every functional block)
These tags define the core interface contract.
* **`@brief`**: Mandatory, a short single-line technical description of its specific action.
    * *Ex:* `@brief Initializes sensor array.`
* **`@details`**: Mandatory,  detailed logical description. Must provide a high-density technical summary detailing critical algorithmic logic, complexity and side effects. Write description for other LLM **Agents**, NOT humans. Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
* **`@param`**: Mandatory is params are defined, input definition. Must include type constraints if the language is dynamic.
    * *Ex:* `@param[in] id Unique identifier (UUIDv4 format).`
* **`@return`** (or **`@retval`**): Mandatory, output definition. Describe the data structure returned in a single block or list specific return values.
    * *Ex:* `@return {bool} True if connection established; structure {x,y} otherwise.`

### B. CONTEXT-MANDATORY TAGS (Required based on logic)
You must analyze the code logic. If these conditions exist, the tag is **Mandatory**.
* **`@param[out]`**: MANDATORY if a reference/pointer argument is mutated inside the function (C/C++).
* **`@exception`** (or **`@throws`**): MANDATORY if the function can raise an exception or error state. List specific error classes.
* **`@satisfies`**: If applicable, link to requirements (e.g., @satisfies REQ-026, REQ-045).

### C. OPTIONAL TAGS (Semantic Enrichment)
Use these to increase context window efficiency for future agents.
* **`@pre`**: Pre-conditions. What must be true *before* calling. Use logical notation.
* **`@post`**: Post-conditions. System state *after* execution.
* **`@warning`**: Critical usage hazards (e.g., non-thread-safe).
* **`@note`**: Vital implementation details not fitting in `@details`.
* **`@see`** (or **`@sa`**): Links to related functions/classes for context linkage.
* **`@deprecated`**: If applicable, link to the replacement API.


## 5) Operational Rules

### Rule A: The "Update" Imperative
If you modify code, you must **immediately** verify and update the associated documentation. Stale documentation is a hallucination trigger and is strictly forbidden.

### Rule B: 100% Coverage
Every exportable symbol must be documented. New code does not exist until it is documented according to the **Tag Taxonomy**.

### Rule C: Content Heuristics (LLM-Optimized)
1.  **Type Precision:** If Python/JS, explicit types are mandatory in `@param` (e.g., `Dict[str, Any]`).
2.  **Complexity:** In `@details`, state Time/Space complexity (e.g., `O(n log n)`).
3.  **Side Effects:** Explicitly state mutations in `@details` or `@post` (e.g., "Resets global timer").

## 6) Examples of Expected Output

### Example A: C++ (BAD - Human Readable - AVOID)
```cpp
/**
 * This function basically checks if the user is valid.
 * It connects to the db and returns true/false.
 * Be careful not to pass a null user!
 */
bool check_user(User u);
```

### Example B: C++ (GOOD - LLM Optimized)
```cpp
/**
 * @brief Validates User credentials against local cache.
 * @details Performs SHA-256 hash comparison. Short-circuits on empty fields.
 * Implementation uses constant-time comparison to prevent timing attacks.
 * @pre Input User object must be initialized.
 * @param[in] u {UserStruct} target_user - Entity to validate. Must contain non-null 'password_hash'.
 * @return {bool} True if credentials match; False if invalid or cache miss.
 * @throws {AuthError} If internal hashing service is unreachable.
 * @note Complexity: O(1) - Constant time lookup.
 * @warning Thread-Safety: Read-only, safe for concurrent calls.
 * @see User::login
 */
bool check_user(User u);
```

### Example C: Python (BAD - Human Readable - AVOID)

```python
def process_telemetry(data, threshold=10):
    """
    Takes some data and cleans it up.
    Removes the old keys and returns a list of numbers.
    Might crash if data is bad.
    """
    # ...
```

### Example D: Python (GOOD - LLM Optimized)

```python
def process_telemetry(data: Dict[str, Any], threshold: int = 10) -> List[float]:
    """
    @brief Filters and normalizes input telemetry stream.
    @details Applies Z-score normalization. Drops keys matching 'legacy_*' pattern.
    Uses list comprehension for memory efficiency.
    @pre 'data' dictionary must not be empty.
    @param data {Dict[str, Any]} Raw JSON payload from sensor.
    @param threshold {int} Noise cutoff value. Defaults to 10.
    @return {List[float]} Normalized value sequence in range [0.0, 1.0].
    @throws {ValueError} If calculated standard deviation is zero.
    @complexity O(N) where N is the number of keys in 'data'.
    @side_effect Logs warning if >50% of data is filtered out.
    """
    # Implementation...
```


# Doxygen: Documenting the code
This chapter covers two topics:

1.  How to put comments in your code such that Doxygen incorporates them in the documentation it generates. This is further detailed in the [next section](#specialblock "Special comment blocks").
2.  Ways to structure the contents of a comment block such that the output looks good, as explained in section [Anatomy of a comment block](#docstructure "Anatomy of a comment block").

Special comment blocks
----------------------

A special comment block is a C or C++ style comment block with some additional markings, so Doxygen knows it is a piece of structured text that needs to end up in the generated documentation. The [next](#cppblock "Comment blocks for C-like languages (C/C++/C#/Objective-C/PHP/Java)") section presents the various styles supported by Doxygen.

For Python, VHDL, and Fortran code there are different commenting conventions, which can be found in sections [Comment blocks in Python](#pythonblocks "Comment blocks in Python"), [Comment blocks in VHDL](#vhdlblocks "Comment blocks in VHDL"), and [Comment blocks in Fortran](#fortranblocks "Comment blocks in Fortran") respectively.

Comment blocks for C-like languages (C/C++/C#/Objective-C/PHP/Java)
-------------------------------------------------------------------

For each entity in the code there are two (or in some cases three) types of descriptions, which together form the documentation for that entity; a _brief_ description and _detailed_ description, both are optional. For methods and functions there is also a third type of description, the so called _in body_ description, which consists of the concatenation of all comment blocks found within the body of the method or function.

Having more than one brief or detailed description is allowed (but not recommended, as the order in which the descriptions will appear is not specified).

As the name suggests, a brief description is a short one-liner, whereas the detailed description provides longer, more detailed documentation. An "in body" description can also act as a detailed description or can describe a collection of implementation details. For the HTML output brief descriptions are also used to provide tooltips at places where an item is referenced.

There are several ways to mark a comment block as a detailed description:

1.  You can use the Javadoc style, which consist of a C-style comment block starting with two \*'s, like this:
    
    ```
/**
 * ... text ...
 */

```

    
2.  or you can use the Qt style and add an exclamation mark (!) after the opening of a C-style comment block, as shown in this example:
    
    ```
/*!
 * ... text ...
 */

```

    
    In both cases the intermediate \*'s are optional, so
    
    ```
/*!
 ... text ...
*/

```

    
    is also valid.
    
3.  A third alternative is to use a block of _at least two_ C++ comment lines, where each line starts with an additional slash or an exclamation mark. Here are examples of the two cases:
    
    ```
///
/// ... text ...
///

```

    
    or
    
    ```
//!
//!... text ...
//!

```

    
    Note that a blank line ends a documentation block in this case.
    
4.  Some people like to make their comment blocks more visible in the documentation. For this purpose you can use the following:
    
    ```
/*******************************************//**
 *  ... text
 ***********************************************/

```

    
    Note: the 2 slashes to end the normal comment block and start a special comment block.
    
    Note: be careful when using a reformatter like clang-format as it may see this type of comment as 2 separate comments and introduce spacing between them.
    
    or
    
    ```
/////////////////////////////////////////////////
/// ... text ...
/////////////////////////////////////////////////

```

    
    or
    
    ```
/***********************************************
 *  ... text
 ***********************************************/

```

    
    as long as [JAVADOC\_BANNER](about:blank/config.html#cfg_javadoc_banner "cfg_javadoc_banner") is set to `YES`.
    
    void cstyle( int theory );
    
    void javadocBanner( int theory );
    
    void doxygenBanner( int theory );
    
    Click [here](examples/javadoc-banner/html/javadoc-banner_8h.html) for the corresponding HTML documentation that is generated by Doxygen.
    

For the brief description there are also several possibilities:

1.  One could use the [\\brief](about:blank/commands.html#cmdbrief "\\brief { brief description }") command with one of the above comment blocks. This command ends at the end of a paragraph, so the detailed description follows after an empty line.
    
    Here is an example:
    
    ```
/*! \brief Brief description.
 *         Brief description continued.
 *
 *  Detailed description starts here.
 */

```

    
2.  If [JAVADOC\_AUTOBRIEF](about:blank/config.html#cfg_javadoc_autobrief "cfg_javadoc_autobrief") is set to `YES` in the configuration file, then using Javadoc style comment blocks will automatically start a brief description which ends at the first dot, question mark or exclamation mark followed by a space or new line. Here is an example:
    
    ```
/** Brief description which ends at this dot. Details follow
 *  here.
 */

```

    
    The option has the same effect for multi-line special C++ comments:
    
    ```
/// Brief description which ends at this dot. Details follow
/// here.

```

    
3.  A third option is to use a special C++ style comment which does not span more than one line. Here are two examples:
    
    ```
/// Brief description.
/** Detailed description. */

```

    
    or
    
    ```
//! Brief description.

//! Detailed description
//! starts here.

```

    
    Note the blank line in the last example, which is required to separate the brief description from the block containing the detailed description. The [JAVADOC\_AUTOBRIEF](about:blank/config.html#cfg_javadoc_autobrief "cfg_javadoc_autobrief") should also be set to `NO` for this case.
    

As you can see Doxygen is quite flexible. If you have multiple detailed descriptions, like in the following example:

```
//! Brief description, which is
//! really a detailed description since it spans multiple lines.
/*! Another detailed description!
 */

```


They will be joined. Note that this is also the case if the descriptions are at different places in the code! In this case the order will depend on the order in which Doxygen parses the code.

Unlike most other documentation systems, Doxygen also allows you to put the documentation of members (including global functions) in front of the _definition_. This way the documentation can be placed in the source file instead of the header file. This keeps the header file compact and allows the implementer of the members more direct access to the documentation. As a compromise the brief description could be placed before the declaration and the detailed description before the member definition.

### Putting documentation after members

If you want to document the members of a file, struct, union, class, or enum, it is sometimes desired to place the documentation block after the member instead of before. For this purpose you have to put an additional < marker in the comment block. Note that this also works for the parameters of a function.

Here are some examples:

```
int var; /*!< Detailed description after the member */

```


This block can be used to put a Qt style detailed documentation block _after_ a member. Other ways to do the same are:

```
int var; /**< Detailed description after the member */

```


or

```
int var; //!< Detailed description after the member
         //!<

```


or

```
int var; ///< Detailed description after the member
         ///<

```


Most often one only wants to put a brief description after a member. This is done as follows:

```
int var; //!< Brief description after the member

```


or

```
int var; ///< Brief description after the member

```


For functions one can use the [@param](about:blank/commands.html#cmdparam "\\param[\<dir\>] <parameter-name> { parameter description }") command to document the parameters and then use `[in]`, `[out]`, `[in,out]` to document the direction. For inline documentation this is also possible by starting with the direction attribute, e.g.

```
void foo(int v /**< [in] docs for input parameter v. */);

```


Note that these blocks have the same structure and meaning as the special comment blocks in the previous section only the < indicates that the member is located in front of the block instead of after the block.

Here is an example of the use of these comment blocks:

class Afterdoc\_Test

{

public:

enum EnumType

{

int EVal1,

int EVal2

};

void member();

protected:

int value;

};

Click [here](examples/afterdoc/html/class_afterdoc___test.html) for the corresponding HTML documentation that is generated by Doxygen.

Warning

These blocks can only be used to document _members_ and _parameters_. They cannot be used to document files, classes, unions, structs, groups, namespaces, macros, and enums themselves. Furthermore, the structural commands mentioned in the next section (like `\class`) are not allowed inside these comment blocks.

Be careful using this construct as part of a macro definition, because when [MACRO\_EXPANSION](about:blank/config.html#cfg_macro_expansion "cfg_macro_expansion") is set to YES at the places where the macro is applied, also the comment will be substituted and this comment is then used as documentation for the last item encountered and not for the macro definition itself!

### Examples

Here is an example of a documented piece of C++ code using the Qt style:

class QTstyle\_Test

{

public:

enum TEnum {

TVal1,

TVal2,

TVal3

}

\*enumPtr,

enumVar;

QTstyle\_Test();

~QTstyle\_Test();

int testMe(int a,const char \*s);

virtual void testMeToo(char c1,char c2) = 0;

int publicVar;

int (\*handler)(int a,int b);

};

Click [here](examples/qtstyle/html/class_q_tstyle___test.html) for the corresponding HTML documentation that is generated by Doxygen.

The brief descriptions are included in the member overview of a class, namespace or file and are printed using a small italic font (this description can be hidden by setting [BRIEF\_MEMBER\_DESC](about:blank/config.html#cfg_brief_member_desc "cfg_brief_member_desc") to `NO` in the configuration file). By default the brief descriptions become the first sentence of the detailed descriptions (but this can be changed by setting the [REPEAT\_BRIEF](about:blank/config.html#cfg_repeat_brief "cfg_repeat_brief") tag to `NO`). Both the brief and the detailed descriptions are optional for the Qt style.

By default a Javadoc style documentation block behaves the same way as a Qt style documentation block. This is not according the Javadoc specification however, where the first sentence of the documentation block is automatically treated as a brief description. To enable this behavior, you should set [JAVADOC\_AUTOBRIEF](about:blank/config.html#cfg_javadoc_autobrief "cfg_javadoc_autobrief") to YES in the configuration file. If you enable this option and want to put a dot in the middle of a sentence without ending it, you should put a backslash and a space after it. Here is an example:

```
  /** Brief description (e.g.\ using only a few words). Details follow. */

```


Here is the same piece of code as shown above, this time documented using the Javadoc style and [JAVADOC\_AUTOBRIEF](about:blank/config.html#cfg_javadoc_autobrief "cfg_javadoc_autobrief") set to YES:

class Javadoc\_Test

{

public:

enum TEnum {

TVal1,

TVal2,

TVal3

}

\*enumPtr,

enumVar;

Javadoc\_Test();

~Javadoc\_Test();

int testMe(int a,const char \*s);

virtual void testMeToo(char c1,char c2) = 0;

int publicVar;

int (\*handler)(int a,int b);

};

Click [here](examples/jdstyle/html/class_javadoc___test.html) for the corresponding HTML documentation that is generated by Doxygen.

Similarly, if one wishes the first sentence of a Qt style documentation block to automatically be treated as a brief description, one may set [QT\_AUTOBRIEF](about:blank/config.html#cfg_qt_autobrief "cfg_qt_autobrief") to YES in the configuration file.

### Documentation at other places

In the examples in the previous section, the comment blocks were always located _in front_ of the declaration or definition of a file, class or namespace or _in front_ or _after_ one of its members. Although this is often comfortable, there may sometimes be reasons to put the documentation somewhere else. For documenting a file this is even required since there is no such thing as "in front of a file".

Doxygen allows you to put your documentation blocks practically anywhere (the exception is inside the body of a function or inside a normal C style comment block).

The price you pay for not putting the documentation block directly before (or after) an item is the need to put a structural command inside the documentation block, which leads to some duplication of information. So in practice you should _avoid_ the use of structural commands _unless_ other requirements force you to do so.

Structural commands (like [all other commands](about:blank/commands.html#cmd_intro "Introduction")) start with a backslash (\\), or an at-sign (@) if you prefer Javadoc style, followed by a command name and one or more parameters. For instance, if you want to document the class `Test` in the example above, you could have also put the following documentation block somewhere in the input that is read by Doxygen:

```
/*! \class Test
    \brief A test class.

    A more detailed class description.
*/

```


Here the special command `\class` is used to indicate that the comment block contains documentation for the class `Test`. Other structural commands are:

*   `\struct` to document a C-struct.
*   `\union` to document a union.
*   `\enum` to document an enumeration type.
*   `\fn` to document a function.
*   `\var` to document a variable or typedef or enum value.
*   `\def` to document a #define.
*   `\typedef` to document a type definition.
*   `\file` to document a file.
*   `\namespace` to document a namespace.
*   `\package` to document a Java package.
*   `\interface` to document an IDL interface.

See section [Special Commands](commands.html "Special Commands") for detailed information about these and many other commands.

To document a member of a C++ class, you must also document the class itself. The same holds for namespaces. To document a global C function, typedef, enum or preprocessor definition you must first document the file that contains it (usually this will be a header file, because that file contains the information that is exported to other source files).

Attention

Let's repeat that, because it is often overlooked: to document global objects (functions, typedefs, enum, macros, etc), you _must_ document the file in which they are defined. In other words, there _must_ at least be a

```
/*! \file */ 
```


or a

```
/** @file */ 
```


line in this file.

Here is an example of a C header named `structcmd.h` that is documented using structural commands:

#define MAX(a,b) (((a)>(b))?(a):(b))

typedef unsigned int UINT32;

int errno;

int open(const char \*,int);

int close(int);

size\_t write(int,const char \*, size\_t);

int read(int,char \*,size\_t);

Click [here](examples/structcmd/html/structcmd_8h.html) for the corresponding HTML documentation that is generated by Doxygen.

Because each comment block in the example above contains a structural command, all the comment blocks could be moved to another location or input file (the source file for instance), without affecting the generated documentation. The disadvantage of this approach is that prototypes are duplicated, so all changes have to be made twice! Because of this you should first consider if this is really needed, and avoid structural commands if possible. I often receive examples that contain the \\fn command in comment blocks which are placed in front of a function. This is clearly a case where the \\fn command is redundant and will only lead to problems.

When you place a comment block in a file with one of the following extensions .dox, .txt, .doc, .md or .markdown or when the extension maps to md by means of the [EXTENSION\_MAPPING](about:blank/config.html#cfg_extension_mapping "cfg_extension_mapping") then Doxygen will hide this file from the file list.

If you have a file that Doxygen cannot parse but you still would like to document it, you can show it as-is using [\\verbinclude](about:blank/commands.html#cmdverbinclude "\\verbinclude <file-name>"), e.g.

```
/*! \file myscript.sh
 *  Look at this nice script:
 *  \verbinclude myscript.sh
 */

```


Make sure that the script is explicitly listed in the [INPUT](about:blank/config.html#cfg_input "cfg_input") or that [FILE\_PATTERNS](about:blank/config.html#cfg_file_patterns "cfg_file_patterns") includes the .sh extension and the script can be found in the path set via [EXAMPLE\_PATH](about:blank/config.html#cfg_example_path "cfg_example_path").

Comment blocks in Python
------------------------

For Python there is a standard way of documenting the code using so called documentation strings ("""). Such strings are stored in `__doc__` and can be retrieved at runtime. Doxygen will extract such comments and assume they have to be represented in a preformatted way.

"""@package docstring

Documentation for this module.

More details.

"""

def func():

"""Documentation for a function.

More details.

"""

pass

class PyClass:

"""Documentation for a class.

More details.

"""

def \_\_init\_\_(self):

"""The constructor."""

self.\_memVar = 0;

def PyMethod(self):

"""Documentation for a method."""

pass

Click [here](examples/docstring/html/namespacedocstring.html) for the corresponding HTML documentation that is generated by Doxygen.

Note

When using """ none of Doxygen's [special commands](about:blank/commands.html#cmd_intro "Introduction") are supported and the text is shown as verbatim text see [\\verbatim](about:blank/commands.html#cmdverbatim "\\verbatim"). To have the Doxygen's [special commands](about:blank/commands.html#cmd_intro "Introduction") and have the text as regular documentation instead of """ use """! or set [PYTHON\_DOCSTRING](about:blank/config.html#cfg_python_docstring "cfg_python_docstring") to `NO` in the configuration file.

Instead of """ one can also use '''.

There is also another way to document Python code using comments that start with "##" or "##<". These types of comment blocks are more in line with the way documentation blocks work for the other languages supported by Doxygen and this also allows the use of special commands.

Here is the same example again but now using Doxygen style comments:

def func():

pass

class PyClass:

def \_\_init\_\_(self):

self.\_memVar = 0;

def PyMethod(self):

pass

classVar = 0;

Click [here](examples/pyexample/html/namespacepyexample.html) for the corresponding HTML documentation that is generated by Doxygen.

Since Python looks more like Java than like C or C++, you should set [OPTIMIZE\_OUTPUT\_JAVA](about:blank/config.html#cfg_optimize_output_java "cfg_optimize_output_java") to `YES` in the configuration file.

Comment blocks in VHDL
----------------------

For VHDL a comment normally starts with "--". Doxygen will extract comments starting with "--!". There are only two types of comment blocks in VHDL; a one line "--!" comment representing a brief description, and a multi-line "--!" comment (where the "--!" prefix is repeated for each line) representing a detailed description.

Comments are always located in front of the item that is being documented with one exception: for ports the comment can also be after the item and is then treated as a brief description for the port.

Here is an example VHDL file with Doxygen comments:

library ieee;

use ieee.std\_logic\_1164.all;

entity mux\_using\_with is

port (

din\_0 : in std\_logic;

din\_1 : in std\_logic;

sel : in std\_logic;

mux\_out : out std\_logic

);

end entity;

architecture behavior of mux\_using\_with is

begin

with (sel) select

mux\_out <= din\_0 when '0',

din\_1 when others;

end architecture;

Click [here](examples/mux/html/mux_8vhdl.html) for the corresponding HTML documentation that is generated by Doxygen.

As of VHDL 2008, it is also possible to use /\`\`\* style comments.  
Doxygen will handle /\`\`\* ... \*\`\`/as plain comments and /\`\`\*! ... \*\`\`/ style comments as special comments to be parsed by Doxygen.

To get proper looking output you need to set [OPTIMIZE\_OUTPUT\_VHDL](about:blank/config.html#cfg_optimize_output_vhdl "cfg_optimize_output_vhdl") to `YES` in the configuration file. This will also affect a number of other settings. When they were not already set correctly Doxygen will produce a warning telling which settings were overruled.

Comment blocks in Fortran
-------------------------

When using Doxygen for Fortran code you should set [OPTIMIZE\_FOR\_FORTRAN](about:blank/config.html#cfg_optimize_for_fortran "cfg_optimize_for_fortran") to `YES`.

The parser tries to guess if the source code is fixed format Fortran or free format Fortran code. This may not always be correct. If not one should use [EXTENSION\_MAPPING](about:blank/config.html#cfg_extension_mapping "cfg_extension_mapping") to correct this. By setting EXTENSION\_MAPPING = f=FortranFixed f90=FortranFree files with extension `f` are interpreted as fixed format Fortran code and files with extension `f90` are interpreted as free format Fortran code.

For Fortran "!>" or "!<" starts a comment and "!!" or "!>" can be used to continue an one line comment into a multi-line comment.

Here is an example of a documented Fortran subroutine:

subroutine intrestbuild(A,aggr,Restrict,A\_ghost)

implicit none

Type(SpMtx), intent(in) :: A

Type(Aggrs), intent(in) :: aggr

Type(SpMtx), intent(out) :: Restrict

end subroutine

As an alternative you can also use comments in fixed format code:

function a(i)

integer i

end function A

Anatomy of a comment block
--------------------------

The previous section focused on how to make the comments in your code known to Doxygen, it explained the difference between a brief and a detailed description, and the use of structural commands.

In this section we look at the contents of the comment block itself.

Doxygen supports various styles of formatting your comments.

The simplest form is to use plain text. This will appear as-is in the output and is ideal for a short description.

For longer descriptions you often will find the need for some more structure, like a block of verbatim text, a list, or a simple table. For this Doxygen supports the [Markdown](https://daringfireball.net/projects/markdown/syntax) syntax, including parts of the [Markdown Extra](https://michelf.ca/projects/php-markdown/extra/) extension.

Markdown is designed to be very easy to read and write. Its formatting is inspired by plain text mail. Markdown works great for simple, generic formatting, like an introduction page for your project. Doxygen also supports reading of markdown files directly. For more details see chapter [Markdown support](markdown.html "Markdown support").



# Doxygen: Markdown support
[Markdown](https://daringfireball.net/projects/markdown/) support was introduced in Doxygen version 1.8.0. It is a plain text formatting syntax written by John Gruber, with the following underlying design goal:

> The design goal for Markdown's formatting syntax is to make it as readable as possible. The idea is that a Markdown-formatted document should be publishable as-is, as plain text, without looking like it's been marked up with tags or formatting instructions. While Markdown's syntax has been influenced by several existing text-to-HTML filters, the single biggest source of inspiration for Markdown's syntax is the format of plain text email.

In the [next section](#markdown_std "Standard Markdown") the standard Markdown features are briefly discussed. The reader is referred to the [Markdown site](https://daringfireball.net/projects/markdown/) for more details.

Some enhancements were made, for instance [PHP Markdown Extra](https://michelf.ca/projects/php-markdown/extra/), and [GitHub flavored Markdown](https://github.github.com/github-flavored-markdown/). The section [Markdown Extensions](#markdown_extra "Markdown Extensions") discusses the extensions that Doxygen supports.

Finally section [Doxygen specifics](#markdown_dox "Doxygen specifics") discusses some specifics for Doxygen's implementation of the Markdown standard.

Standard Markdown
-----------------

Paragraphs
----------

Even before Doxygen had Markdown support it supported the same way of paragraph handling as Markdown: to make a paragraph you just separate consecutive lines of text by one or more blank lines.

An example:

```
Here is text for one paragraph.

We continue with more text in another paragraph.

```


Headers
-------

Just like Markdown, Doxygen supports two types of headers

Level 1 or 2 headers can be made as the follows

```
This is a level 1 header
========================

This is a level 2 header
------------------------

```


A header is followed by a line containing only ='s or -'s. Note that the exact amount of ='s or -'s is not important as long as there are at least two.

Alternatively, you can use #'s at the start of a line to make a header. The number of #'s at the start of the line determines the level (up to 6 levels are supported). You can end a header by any number of #'s.

Here is an example:

```
# This is a level 1 header

### This is level 3 header #######

```


Block quotes
------------

Block quotes can be created by starting each line with one or more >'s, similar to what is used in text-only emails.

```
> This is a block quote
> spanning multiple lines

```


Lists and code blocks (see below) can appear inside a quote block. Quote blocks can also be nested.

Note that Doxygen requires that you put a space after the (last) > character to avoid false positives, i.e. when writing

```
0  if OK\n
>1 if NOK

```


the second line will not be seen as a block quote.

Lists
-----

Simple bullet lists can be made by starting a line with -, +, or \*.

```
- Item 1

  More text for this item.

- Item 2
  + nested list item.
  + another nested item.
- Item 3

```


List items can span multiple paragraphs (if each paragraph starts with the proper indentation) and lists can be nested. You can also make a numbered list like so

```
1. First item.
2. Second item.

```


Make sure to also read [Lists Extensions](#mddox_lists "Lists Extensions") for Doxygen specifics.

Code Blocks
-----------

Preformatted verbatim blocks can be created by indenting each line in a block of text by at least 4 extra spaces

```
This a normal paragraph

    This is a code block

We continue with a normal paragraph again.

```


Doxygen will remove the mandatory indentation from the code block. Note that you cannot start a code block in the middle of a paragraph (i.e. the line preceding the code block must be empty).

See section [Code Block Indentation](#mddox_code_blocks "Code Block Indentation") for more info how Doxygen handles indentation as this is slightly different than standard Markdown.

Horizontal Rulers
-----------------

A horizontal ruler will be produced for lines containing at least three or more hyphens, asterisks, or underscores. The line may also include any amount of whitespace.

Examples:

```
- - -
______

```


Note that using asterisks in comment blocks does not work. See [Use of asterisks](#mddox_stars "Use of asterisks") for details.  
Note that when using hyphens and the previous line is not empty you have to use at least one whitespace in the sequence of hyphens otherwise it might be seen as a level 2 header (see [Headers](#md_headers "Headers")).

Emphasis
--------

To emphasize a text fragment you start and end the fragment with an underscore or star. Using two stars or underscores will produce strong emphasis. Three stars or underscores will combine the emphasis from the previous two options.

Examples:

```
 *single asterisks*

 _single underscores_

 **double asterisks**

 __double underscores__

 ***triple asterisks***

 ___triple underscores___

```


See section [Emphasis and strikethrough limits](#mddox_emph_spans "Emphasis and strikethrough limits") for more info how Doxygen handles emphasis / strikethrough spans slightly different than standard / Markdown GitHub Flavored Markdown.

Strikethrough
-------------

To strikethrough a text fragment you start and end the fragment with two tildes.

Examples:

```
 ~~double tilde~~

```


See section [Emphasis and strikethrough limits](#mddox_emph_spans "Emphasis and strikethrough limits") for more info how Doxygen handles emphasis / strikethrough spans slightly different than standard Markdown / GitHub Flavored Markdown.

code spans
----------

To indicate a span of code, you should wrap it in backticks ( \` ). Unlike code blocks, code spans appear inline in a paragraph. An example:

```
Use the `printf()` function.

```


To show a literal backtick or single quote inside a code span use double backticks, i.e.

```
To assign the output of command `ls` to `var` use ``var=`ls```.

To assign the text 'text' to `var` use ``var='text'``.

```


See section [Code Spans Limits](#mddox_code_spans "Code Spans Limits") for more info how Doxygen handles code spans slightly different than standard Markdown.

Links
-----

Doxygen supports both styles of make links defined by Markdown: _inline_ and _reference_.

For both styles the link definition starts with the link text delimited by \[square brackets\].

### Inline Links

For an inline link the link text is followed by a URL and an optional link title which together are enclosed in a set of regular parenthesis. The link title itself is surrounded by quotes.

Examples:

```
[The link text](http://example.net/)
[The link text](http://example.net/ "Link title")
[The link text](https://www.doxygen.nl/relative/path/to/index.html "Link title")
[The link text](somefile.html)

```


In addition Doxygen provides a similar way to link a documented entity:

```
[The link text](@ref MyClass)

```


in case the first non whitespace character of the reference is a `#` this is interpreted as a Doxygen link and replaced as a [@ref](about:blank/commands.html#cmdref "\\ref \<name\> [\"(text)\"]") command:

```
[The link text](#MyClass)

```


will be interpreted as:

```
@ref MyClass "The link text"

```


### Reference Links

Instead of putting the URL inline, you can also define the link separately and then refer to it from within the text.

The link definition looks as follows:

```
[link name]: http://www.example.com "Optional title"

```


Instead of double quotes also single quotes or parenthesis can be used for the title part.

Once defined, the link looks as follows

```
[link text][link name]

```


If the link text and name are the same, also

```
[link name][]

```


or even

```
[link name]

```


can be used to refer to the link. Note that the link name matching is not case sensitive as is shown in the following example:

```
I get 10 times more traffic from [Google] than from
[Yahoo] or [MSN].

[google]: http://google.com/        "Google"
[yahoo]:  http://search.yahoo.com/  "Yahoo Search"
[msn]:    http://search.msn.com/    "MSN Search"

```


Link definitions will not be visible in the output.

Like for inline links Doxygen also supports @ref inside a link definition:

```
[myclass]: @ref MyClass "My class"

```


Images
------

Markdown syntax for images is similar to that for links. The only difference is an additional ! before the link text.

Examples:

```
![Caption text](https://www.doxygen.nl/path/to/img.jpg)
![Caption text](https://www.doxygen.nl/path/to/img.jpg "Image title")
![Caption text][img def]
![img def]

[img def]: /path/to/img.jpg "Optional Title"

```


Also here you can use @ref to link to an image:

```
![Caption text](@ref image.png)
![img def]

[img def]: @ref image.png "Caption text"

```


The caption text is optional.

Note

Don't forget to add the path of the image to the [IMAGE\_PATH](about:blank/config.html#cfg_image_path "cfg_image_path").

Automatic Linking
-----------------

To create a link to an URL or e-mail address Markdown supports the following syntax:

```
<http://www.example.com>
<https://www.example.com>
<ftp://www.example.com>
<mailto:[email protected]>
<[email protected]>

```


Note that Doxygen will also produce the links without the angle brackets.

Markdown Extensions
-------------------

Table of Contents
-----------------

Doxygen supports a special link marker \[TOC\] which can be placed in a page to produce a table of contents at the start of the page, listing all sections.

Note that using \[TOC\] is the same as using a [\\tableofcontents](about:blank/commands.html#cmdtableofcontents "\\tableofcontents['{'[option[:level]][,option[:level]]*'}']") command.

Note that the [TOC\_INCLUDE\_HEADINGS](about:blank/config.html#cfg_toc_include_headings "cfg_toc_include_headings") has to be set to a value > 0 otherwise no table of contents is shown when using [Markdown Headers](#md_headers "Headers").

Tables
------

Of the features defined by "Markdown Extra" is support for [simple tables](https://michelf.ca/projects/php-markdown/extra/#table):

A table consists of a header line, a separator line, and at least one row line. Table columns are separated by the pipe (|) character.

Here is an example:

```
First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

```


which will produce the following table:


|First Header  |Second Header  |
|--------------|---------------|
|Content Cell  |Content Cell   |
|Content Cell  |Content Cell   |


Column alignment can be controlled via one or two colons at the header separator line:

```
| Right | Center | Left  |
| ----: | :----: | :---- |
| 10    | 10     | 10    |
| 1000  | 1000   | 1000  |

```


which will look as follows:


|Right  |Center  |Left  |
|-------|--------|------|
|10     |10      |10    |
|1000   |1000    |1000  |


Additionally, column and row spans are supported. Using a caret ("^") in a cell indicates that the cell above should span rows. Sequences of carets may be used for any number of row spans. For example:

```
| Right | Center | Left  |
| ----: | :----: | :---- |
| 10    | 10     | 10    |
| ^     | 1000   | 1000  |

```


which will look as follows:


|Right  |Center  |Left  |
|-------|--------|------|
|10     |10      |10    |
|1000   |1000    |      |


Column spans are supported by means of directly adjacent vertical bars ("|"). Each additional vertical bar indicates an additional column to be spanned. To put it another way, a single vertical bar indicates a single column span, two vertical bars indicates a 2 columns span, and so on. For example:

```
| Right | Center | Left  |
| ----: | :----: | :---- |
| 10    | 10     | 10    |
| 1000  |||

```


which will look as follows:


|Right  |Center  |Left  |
|-------|--------|------|
|10     |10      |10    |
|1000   |        |      |


For more complex tables in Doxygen please have a look at: [Including tables](tables.html "Including tables")

Fenced Code Blocks
------------------

Another feature defined by "Markdown Extra" is support for [fenced code blocks](https://michelf.ca/projects/php-markdown/extra/#fenced-code-blocks):

A fenced code block does not require indentation, and is defined by a pair of "fence lines". Such a line consists of 3 or more tilde (~) characters on a line. The end of the block should have the same number of tildes. Here is an example:

```
This is a paragraph introducing:

~~~~~~~~~~~~~~~~~~~~~
a one-line code block
~~~~~~~~~~~~~~~~~~~~~

```


By default the output is the same as for a normal code block.

For languages supported by Doxygen you can also make the code block appear with syntax highlighting. To do so you need to indicate the typical file extension that corresponds to the programming language after the opening fence. For highlighting according to the Python language for instance, you would need to write the following:

```
~~~~~~~~~~~~~{.py}
# A class
class Dummy:
    pass
~~~~~~~~~~~~~

```


which will produce:

and for C you would write:

```
~~~~~~~~~~~~~~~{.c}
int func(int a,int b) { return a*b; }
~~~~~~~~~~~~~~~

```


which will produce:

int func(int a,int b) { return a\*b; }

The dot is optional, the curly braces are optional when the that language name begins with an alphabetical character and further characters are alphanumerical characters or a plus sign.

Another way to denote fenced code blocks is to use 3 or more backticks (\`\`\`):

\`\`\`

also a fenced code block

\`\`\`

For the image formats dot, msc and plantuml the fenced block will be shown as an image provided the image format is enabled (see [HAVE\_DOT](about:blank/config.html#cfg_have_dot "cfg_have_dot") and [PLANTUML\_JAR\_PATH](about:blank/config.html#cfg_plantuml_jar_path "cfg_plantuml_jar_path")), otherwise it is shown as plain code.

Example:

\`\`\`plantuml

Alice -> Bob

\`\`\`

or

\`\`\`plantuml

@startuml

Alice -> Bob

@enduml

\`\`\`

Header Id Attributes
--------------------

Standard Markdown has no support for labeling headers, which is a problem if you want to link to a section.

PHP Markdown Extra allows you to label a header by adding the following to the header

```
Header 1                {#labelid}
========

## Header 2 ##          {#labelid2}

```


To link to a section in the same comment block you can use

```
[Link text](#labelid)

```


to link to a section in general, Doxygen allows you to use [@ref](about:blank/commands.html#cmdref "\\ref \<name\> [\"(text)\"]")

```
[Link text](@ref labelid)

```


Note this only works for the headers of level 1 to 4.

Image Attributes
----------------

Standard Markdown has no support for controlling image dimensions which results in less flexibility when writing docs.

PHP Markdown Extra allows you to add extra attributes to an image as in:

```
![Caption text](https://www.doxygen.nl/path/to/img.jpg){attributes}

```


To allow for output format specific attributes the following syntax is supported

```
![Caption text](https://www.doxygen.nl/path/to/img.jpg){format: attributes, format: attributes}

```


For a description of the possibilities see the paragraph [Size indication](about:blank/commands.html#image_sizeindicator "image_sizeindicator") for the [\\image](about:blank/commands.html#cmdimage "\\image['{'option[,option]'}'] \<format\> \<file\> [\"caption\"] [\<sizeindication\>=\<size\>]") command.

For example:

```
![Doxygen Logo](https://www.doxygen.org/images/doxygen.png){html: width=50%, latex: width=5cm}

```


Doxygen specifics
-----------------

Even though Doxygen tries to following the Markdown standard as closely as possible, there are couple of deviation and Doxygen specifics additions.

Including Markdown files as pages
---------------------------------

Doxygen can process files with Markdown formatting. For this to work the extension for such a file should be .md or .markdown (see [EXTENSION\_MAPPING](about:blank/config.html#cfg_extension_mapping "cfg_extension_mapping") if your Markdown files have a different extension, and use md as the name of the parser). Each file is converted to a page (see the [page](about:blank/commands.html#cmdpage "\\page \<name\> (title)") command for details). Doxygen will not create a dedicated page if the Markdown file starts with a dedicated command (a.o. \\defgroup, \\dir) to avoid creating an empty page when the file only contains directory or group documentation. A README.md file in a subdirectory will be treated as directory documentation, unless it is explicitly overruled by a dedicated command (a.o. @page, @mainpage) to create a new page.

By default the name and title of the page are derived from the file name. If the file starts with a level 1 header however, it is used as the title of the page. If you specify a label for the header (as shown in [Header Id Attributes](#md_header_id "Header Id Attributes")) Doxygen will use that as the page name.

If the label is called index or mainpage Doxygen will put the documentation on the front page (index.html).

Here is an example of a file README.md that will appear as the main page when processed by Doxygen:

```
My Main Page                         {#mainpage}
============

Documentation that will appear on the main page

```


If a page has a label you can link to it using [@ref](about:blank/commands.html#cmdref "\\ref \<name\> [\"(text)\"]") as is shown above. To refer to a markdown page without such label you can simple use the file name of the page, e.g.

```
See [the other page](other.md) for more info.

```


Treatment of HTML blocks
------------------------

Markdown is quite strict in the way it processes block-level HTML:

> block-level HTML elements — e.g. <div>, <table>, <pre>, <p>, etc. — must be separated from surrounding content by blank lines, and the start and end tags of the block should not be indented with tabs or spaces.

Doxygen does not have this requirement, and will also process Markdown formatting inside such HTML blocks. The only exception is <pre> blocks, which are passed untouched (handy for ASCII art).

Doxygen will not process Markdown formatting inside verbatim or code blocks, and in other sections that need to be processed without changes (for instance formulas or inline dot graphs).

Code Block Indentation
----------------------

Markdown allows both a single tab or 4 spaces to start a code block. Since Doxygen already replaces tabs by spaces before doing Markdown processing, the effect will only be same if TAB\_SIZE in the configuration file has been set to 4. When it is set to a higher value spaces will be present in the code block. A lower value will prevent a single tab to be interpreted as the start of a code block.

With Markdown any block that is indented by 4 spaces (and 8 spaces inside lists) is treated as a code block. This indentation amount is absolute, i.e. counting from the start of the line.

Since Doxygen comments can appear at any indentation level that is required by the programming language, it uses a relative indentation instead. The amount of indentation is counted relative to the preceding paragraph. In case there is no preceding paragraph (i.e. you want to start with a code block), the minimal amount of indentation of the whole comment block is used as a reference.

In most cases this difference does not result in different output. Only if you play with the indentation of paragraphs the difference is noticeable:

```
text

 text

  text

   code

```


In this case Markdown will put the word code in a code block, whereas Doxygen will treat it as normal text, since although the absolute indentation is 4, the indentation with respect to the previous paragraph is only 1.

Note that list markers are not counted when determining the relative indent:

```
1.  Item1

    More text for item1

2.  Item2

        Code block for item2

```


For Item1 the indentation is 4 (when treating the list marker as whitespace), so the next paragraph "More text..." starts at the same indentation level and is therefore not seen as a code block.

Emphasis and strikethrough limits
---------------------------------

Unlike standard Markdown and GitHub Flavored Markdown Doxygen will not touch internal underscores or stars or tildes, so the following will appear as-is:

```
a_nice_identifier

```


Furthermore, a \* or \_ only starts an emphasis and a ~ only starts a strikethrough if

*   it is followed by an alphanumerical character, and
*   it is preceded by a space, newline, or one of the following characters <{(\[,:;

An emphasis or a strikethrough ends if

*   it is not followed by an alphanumerical character, and
*   it is not preceded by a space, newline, or one the following characters ({\[<=+-\\@

The span of the emphasis or strikethrough is limited to a single paragraph.

Lastly, note that when you want to put emphasis on a piece of text at the start of a line by means of \*s within a C-style Doxygen comment block (i.e. /\`\`\*\* ... \*\`\`/) that does not have leading \* as column "lineup", then Doxygen will see the sequence of \*s at the beginning of the line as "lineup" and not as emphasis. So the following will not render as bold:

```
/**
 **this is not bold**
 */

```


however this will render as bold:

```
/**
 * **this is bold**
 */

```


Code Spans Limits
-----------------

Note that unlike standard Markdown, Doxygen leaves the following untouched.

```
A `cool' word in a `nice' sentence.

```


In other words; a single quote cancels the special treatment of a code span wrapped in a pair of backtick characters. This extra restriction was added for backward compatibility reasons.

In case you want to have single quotes inside a code span, don't use one backtick but two backticks around the code span.

Double backticks are also ended by double quotes in the same way.

```
A ``cool'' word in a ``nice'' sentence.

```


Lists Extensions
----------------

With Markdown two lists separated by an empty line are joined together into a single list which can be rather unexpected and many people consider it to be a bug. Doxygen, however, will make two separate lists as you would expect.

Example:

```
- Item1 of list 1
- Item2 of list 1

1. Item1 of list 2
2. Item2 of list 2

```


With Markdown the actual numbers you use to mark the list have no effect on the HTML output Markdown produces. I.e. standard Markdown treats the following as one list with 3 numbered items:

```
1. Item1
1. Item2
1. Item3

```


Doxygen however requires that the numbers used as marks are in strictly ascending order, so the above example would produce 3 lists with one item. An item with an equal or lower number than the preceding item, will start a new list. For example:

```
1. Item1 of list 1
3. Item2 of list 1
2. Item1 of list 2
4. Item2 of list 2

```


will produce:

1.  Item1 of list 1
2.  Item2 of list 1

1.  Item1 of list 2
2.  Item2 of list 2

Historically Doxygen has an additional way to create numbered lists by using \-# markers:

```
-# item1
-# item2

```


Lists with as indicator a checked or unchecked check box are by using \- \[ \] or \- \[x\] or \- \[X\] as markers:

```
- [ ] unchecked
- [x] checked

```


Use of asterisks
----------------

Special care has to be taken when using \*'s in a comment block to start a list or make a ruler.

Doxygen will strip off any leading \*'s from the comment before doing Markdown processing. So although the following works fine

```
    /** A list:
     *  * item1
     *  * item2
     */

```


When you remove the leading \*'s Doxygen will strip the other stars as well, making the list disappear!

Rulers created with \*'s will not be visible at all. They only work in Markdown files.

Limits on markup scope
----------------------

To avoid that a stray \* or \_ matches something many paragraphs later, and shows everything in between with emphasis, Doxygen limits the scope of a \* and \_ to a single paragraph.

For a code span, between the starting and ending backtick only two new lines are allowed.

Also for links there are limits; the link text, and link title each can contain only one new line, the URL may not contain any newlines.

Support for GitHub Alerts
-------------------------

In the GitHub version of markdown there is the support for so called alerts, the syntax is similar to a one level block quote followed by \[!<alert>\] where <alert> can be one of note, warning, tip, caution or important. In Doxygen these alerts are translated into normal Doxygen commands:

*   \> \[!note\] is translated to [\\note](about:blank/commands.html#cmdnote "\\note { text }")
*   \> \[!warning\] is translated to [\\warning](about:blank/commands.html#cmdwarning "\\warning { warning message }")
*   \> \[!tip\] is translated to [\\remark](about:blank/commands.html#cmdremark "\\remark { remark text }")
*   \> \[!caution\] is translated to [\\attention](about:blank/commands.html#cmdattention "\\attention { attention text }")
*   \> \[!important\] is translated to [\\important](about:blank/commands.html#cmdimportant "\\important { important text }")

Example:

\> \[!note\]

\> The special text for the note

which will render as:

Note

The special text for the note

Debugging problems
------------------

When Doxygen parses the source code it first extracts the comments blocks, then passes these through the Markdown preprocessor. The output of the Markdown preprocessing consists of text with [special commands](about:blank/commands.html#cmd_intro "Introduction") and [HTML commands](htmlcmds.html "HTML Commands"). A second pass takes the output of the Markdown preprocessor and converts it into the various output formats.

During Markdown preprocessing no errors are produced. Anything that does not fit the Markdown syntax is simply passed on as-is. In the subsequent parsing phase this could lead to errors, which may not always be obvious as they are based on the intermediate format.

To see the result after Markdown processing you can run Doxygen with the \-d Markdown option. It will then print each comment block before and after Markdown processing.


# Doxygen: Lists
Doxygen provides a number of ways to create lists of items.

**Using dashes**

By putting a number of column-aligned minus (\-) signs at the start of a line, a bullet list will automatically be generated. Instead of the minus sign also plus (+) or asterisk (\*) can be used.

Numbered lists can also be generated by using a minus followed by a hash (#) or by using a number followed by a dot.

Lists with as indicator a checked or unchecked check box are possible when having a minus followed by optional spaces and followed by \[ \] for an unchecked check box and \[x\] or \[X\] for a checked check box.

Nesting of lists is allowed and is based on indentation of the items.

Here is an example:

```
  /*! 
   *  A list of events:
   *    - mouse events
   *         -# mouse move event
   *         -# mouse click event\n
   *            More info about the click event.
   *         -# mouse double click event
   *    - keyboard events
   *         1. key down event
   *         2. key up event
   *    - checkbox list
   *         - [ ] unchecked
   *         - [x] checked
   *
   *  More text here.
   */

```


The result will be:

A list of events:

*   mouse events
    1.  mouse move event
    2.  mouse click event  
        More info about the click event.
    3.  mouse double click event
*   keyboard events
    1.  key down event
    2.  key up event
*   checkbox list
    
    *   unchecked
    
    *   checked

More text here.

If you use tabs for indentation within lists, please make sure that [TAB\_SIZE](about:blank/config.html#cfg_tab_size "cfg_tab_size") in the configuration file is set to the correct tab size.

You can end a list by starting a new paragraph or by putting a dot (.) on an empty line at the same indentation level as the list you would like to end.

Here is an example that speaks for itself:

```
/**
 * Text before the list
 * - list item 1
 *   - sub item 1
 *     - sub sub item 1
 *     - sub sub item 2
 *     . 
 *     The dot above ends the sub sub item list.
 *
 *     More text for the first sub item
 *   .
 *   The dot above ends the first sub item.
 *
 *   More text for the first list item
 *   - sub item 2
 *   - sub item 3
 * - list item 2
 * .
 * More text in the same paragraph.
 *
 * More text in a new paragraph.
 */

```


**Using HTML commands**

If you like you can also use HTML commands inside the documentation blocks.

Here is the above example with HTML commands:

```
  /*! 
   *  A list of events:
   *  <ul>
   *  <li> mouse events
   *     <ol>
   *     <li>mouse move event
   *     <li>mouse click event<br>
   *         More info about the click event.
   *     <li>mouse double click event
   *     </ol>
   *  <li> keyboard events
   *     <ol>     
   *     <li>key down event
   *     <li>key up event
   *     </ol>
   *  </ul>
   *  More text here.
   */

```


Note

In this case the indentation is not important.

**Using \\arg or \\li**

For compatibility with the Qt Software's internal documentation tool qdoc and with KDoc, Doxygen has two commands that can be used to create simple unnested lists.

See [\\arg](about:blank/commands.html#cmdarg "\\arg { item-description }") and [\\li](about:blank/commands.html#cmdli "\\li { item-description }") for more info.

