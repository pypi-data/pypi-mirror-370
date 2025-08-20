# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors


class NoSuchTableError(Exception):
    """Raised when the table can't be found in the catalog."""


class NoSuchDatabaseError(Exception):
    """Raised when a referenced name-space is not found."""
