#!/usr/bin/perl
# @file fixture_perl.pl
# @brief Comprehensive Perl test fixture for parser validation.
# @details Covers OOP with bless, Moose-like attributes, closures,
#          here-docs, wantarray, dispatch tables, prototypes, AUTOLOAD,
#          and regular expressions.
# Single line comment
=pod

@brief Documentation block for the fixture module.
@details This module demonstrates advanced Perl constructs including
         object-oriented patterns, closures, and metaprogramming.

=cut

package MyPackage;

use strict;
use warnings;
use Carp qw(croak confess);
require Exporter;
use constant MAX_SIZE => 100;
use constant {
    MIN_SIZE => 1,
    DEFAULT_NAME => 'unnamed',
};

# @brief Module version string.
our $VERSION = '1.0.0';

# @brief Symbols exported by default.
our @EXPORT = qw(greet process);

# @brief Symbols available on request.
our @EXPORT_OK = qw(helper format_output);

# ── Constructor and OOP ──────────────────────────────────────────────

=pod

@brief Create a new MyPackage instance.
@param class The class name (implicit first argument).
@param %args Named arguments: name (required), age (optional).
@return Blessed hashref instance.

=cut

sub new {
    my ($class, %args) = @_;
    croak "name is required" unless $args{name};
    my $self = bless {
        name  => $args{name},
        age   => $args{age} || 0,
        _items => [],
        _cache => {},
    }, $class;
    return $self;
}

# @brief Accessor for the name attribute.
# @return The instance name string.
sub name {
    my ($self, $val) = @_;
    if (defined $val) {
        # Setter mode
        $self->{name} = $val;
        return $self;
    }
    return $self->{name};
}

# @brief Check if the instance is in a valid state.
# @return 1 if valid, 0 otherwise.
sub is_valid {
    my ($self) = @_;
    return defined($self->{name}) && length($self->{name}) > 0 ? 1 : 0;
}

# ── Functions ────────────────────────────────────────────────────────

# @brief Print a greeting to stdout.
# @param $name The person's name.
sub greet {
    my ($name) = @_;
    # Validate input before printing
    unless (defined $name) {
        warn "greet called without name";
        return;
    }
    print "Hello $name\n";
}

# @brief Process data and return result.
# @return 1 indicating success.
sub process {
    return 1;
}

# @brief Format output depending on context (list vs scalar).
# @param @items List of items to format.
# @return In list context: formatted items. In scalar: count.
sub format_output {
    my (@items) = @_;
    if (wantarray()) {
        # List context — return formatted items
        return map { uc($_) } @items;
    } else {
        # Scalar context — return count
        return scalar @items;
    }
}

# @brief Standalone helper for internal use.
# @return Always returns "ok".
sub helper {
    return "ok";
}

# ── Regular expression functions ─────────────────────────────────────

# @brief Extract all email addresses from text.
# @param $text Input text to scan.
# @return List of matched email addresses.
sub extract_emails {
    my ($text) = @_;
    my @emails;
    # Match standard email pattern
    while ($text =~ /\b([\w.+-]+@[\w-]+\.[\w.]+)\b/g) {
        push @emails, $1;
    }
    return @emails;
}

# @brief Replace all occurrences of a pattern in text.
# @param $text Input text.
# @param $pattern Regex pattern to find.
# @param $replacement Replacement string.
# @return Modified text with substitutions applied.
sub replace_all {
    my ($text, $pattern, $replacement) = @_;
    $text =~ s/$pattern/$replacement/g;
    return $text;
}

# ── Closure factory ──────────────────────────────────────────────────

# @brief Create a multiplier closure.
# @param $factor The multiplication factor.
# @return Coderef that multiplies its argument by factor.
sub make_multiplier {
    my ($factor) = @_;
    # Capture $factor in the returned closure
    return sub {
        my ($x) = @_;
        return $x * $factor;
    };
}

# ── Dispatch table ───────────────────────────────────────────────────

# @brief Command dispatch table mapping names to handler coderefs.
my %dispatch = (
    add    => sub { $_[0] + $_[1] },
    sub    => sub { $_[0] - $_[1] },
    mul    => sub { $_[0] * $_[1] },
    div    => sub {
        croak "Division by zero" if $_[1] == 0;
        return $_[0] / $_[1];
    },
);

# @brief Execute a named operation from the dispatch table.
# @param $op Operation name (add, sub, mul, div).
# @param $a First operand.
# @param $b Second operand.
# @return Result of the operation.
# @raise Croaks if operation is unknown.
sub dispatch {
    my ($op, $a, $b) = @_;
    my $handler = $dispatch{$op}
        or croak "Unknown operation: $op";
    return $handler->($a, $b);
}

# ── Here-doc ─────────────────────────────────────────────────────────

# @brief Generate a template string using a here-document.
# @param $name Name to insert into the template.
# @return Formatted multi-line string.
sub generate_template {
    my ($name) = @_;
    return <<END_TEMPLATE;
Dear $name,

This is a generated template.
Version: $VERSION
Max size: @{[ MAX_SIZE ]}

Regards,
The System
END_TEMPLATE
}

# ── AUTOLOAD for dynamic dispatch ────────────────────────────────────

# @brief Handle undefined method calls dynamically.
# @details Methods named get_* return the corresponding attribute.
# @param @args Arguments passed to the auto-loaded method.
# @return The attribute value or undef.
sub AUTOLOAD {
    my ($self, @args) = @_;
    our $AUTOLOAD;
    # Extract method name from fully qualified AUTOLOAD
    my $method = $AUTOLOAD;
    $method =~ s/.*:://;
    return if $method eq 'DESTROY';

    if ($method =~ /^get_(\w+)$/) {
        my $attr = $1;
        return $self->{$attr};
    }
    croak "Undefined method: $method";
}

# ── Error handling ───────────────────────────────────────────────────

# @brief Execute a block with error trapping.
# @param $code Coderef to execute.
# @return Result of execution or undef on error.
sub safe_execute {
    my ($code) = @_;
    my $result = eval {
        $code->();
    };
    if ($@) {
        # Log and suppress error
        warn "Caught error: $@";
        return undef;
    }
    return $result;
}

1; # Module must return true

=pod
coverage extension block
=cut
package Extra::One;
package Extra::Two;
package Extra::Three;
package Extra::Four;
use constant RETRY_LIMIT => 5;
use constant API_HOST => 'localhost';
use constant FEATURE_FLAG => 1;
use constant CACHE_SIZE => 256;
use constant DEFAULT_USER => 'guest';
use lib 'lib';

# REQ-COVER-SRS-231 START
# @REQ-COVER-SRS-231 block 1
# @brief Coverage helper construct 1.
# @details Provides deterministic fixture-level Doxygen coverage block 1.
# @param value Input value for helper construct 1.
# @return Output value for helper construct 1.
sub req_cover_perl_1 {
    my ($value) = @_;
    return $value + 1;
}

# @REQ-COVER-SRS-231 block 2
# @brief Coverage helper construct 2.
# @details Provides deterministic fixture-level Doxygen coverage block 2.
# @param value Input value for helper construct 2.
# @return Output value for helper construct 2.
sub req_cover_perl_2 {
    my ($value) = @_;
    return $value + 2;
}

# @REQ-COVER-SRS-231 block 3
# @brief Coverage helper construct 3.
# @details Provides deterministic fixture-level Doxygen coverage block 3.
# @param value Input value for helper construct 3.
# @return Output value for helper construct 3.
sub req_cover_perl_3 {
    my ($value) = @_;
    return $value + 3;
}

# @REQ-COVER-SRS-231 block 4
# @brief Coverage helper construct 4.
# @details Provides deterministic fixture-level Doxygen coverage block 4.
# @param value Input value for helper construct 4.
# @return Output value for helper construct 4.
sub req_cover_perl_4 {
    my ($value) = @_;
    return $value + 4;
}

# @REQ-COVER-SRS-231 block 5
# @brief Coverage helper construct 5.
# @details Provides deterministic fixture-level Doxygen coverage block 5.
# @param value Input value for helper construct 5.
# @return Output value for helper construct 5.
sub req_cover_perl_5 {
    my ($value) = @_;
    return $value + 5;
}

# REQ-COVER-SRS-231 END
