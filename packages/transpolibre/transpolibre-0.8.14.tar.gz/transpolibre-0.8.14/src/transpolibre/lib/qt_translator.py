# src/transpolibre/lib/qt_translator.py
"""
Qt-specific translation handling for .ts files.
Protects Qt syntax elements during translation and validates results.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set, Callable
from collections import defaultdict


class QtTranslator:
    """Handles Qt-specific translation requirements."""

    def __init__(self) -> None:
        """Initialize the Qt translator."""
        # Track accelerators per context to detect conflicts
        self.context_accelerators: Dict[str, Set[str]] = defaultdict(set)
        self.warnings: List[str] = []

    def protect_placeholders(self, text: str) -> str:
        """
        Protect Qt placeholders with unique tokens before translation.

        Args:
            text: Source text with potential placeholders

        Returns:
            Text with placeholders replaced by tokens
        """
        # Protect numbered placeholders (%1, %2, etc.)
        text = re.sub(r"%(\d+)", r"<QT_P\1/>", text)

        # Protect %n placeholder (for plurals)
        text = text.replace("%n", "<QT_PN/>")

        # Protect {variable} style placeholders
        text = re.sub(r"\{(\w+)\}", r"<QT_VAR_\1/>", text)

        return text

    def restore_placeholders(self, text: str) -> str:
        """
        Restore Qt placeholders from tokens after translation.

        Args:
            text: Translated text with tokens

        Returns:
            Text with placeholders restored
        """
        # Restore numbered placeholders
        text = re.sub(r"<QT_P(\d+)/>", r"%\1", text)

        # Restore %n placeholder
        text = text.replace("<QT_PN/>", "%n")

        # Restore {variable} style placeholders
        text = re.sub(r"<QT_VAR_(\w+)/>", r"{\1}", text)

        return text

    def extract_accelerator(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Extract accelerator key from text.

        Args:
            text: Source text with potential accelerator

        Returns:
            Tuple of (text without accelerator, accelerator letter or None)
        """
        # Handle escaped ampersands first (&&)
        text = text.replace("&&", "<QT_AMPAMP/>")

        # Find accelerator
        match = re.search(r"&(\w)", text)
        if match:
            accel_letter = match.group(1)
            # Remove the accelerator
            clean_text = text.replace(f"&{accel_letter}", accel_letter, 1)
        else:
            clean_text = text
            accel_letter = None

        # Restore escaped ampersands
        clean_text = clean_text.replace("<QT_AMPAMP/>", "&&")

        return clean_text, accel_letter

    def assign_accelerator(
        self, text: str, preferred_letter: Optional[str], context: str
    ) -> str:
        """
        Assign an accelerator key to translated text.

        Args:
            text: Translated text without accelerator
            preferred_letter: The original accelerator letter (if any)
            context: The context name (for conflict detection)

        Returns:
            Text with accelerator assigned
        """
        if not preferred_letter:
            return text

        # Handle escaped ampersands
        text = text.replace("&&", "<QT_AMPAMP/>")

        # Try to use the same letter if it exists in translation
        preferred_lower = preferred_letter.lower()
        text_lower = text.lower()

        assigned = False

        # First try: same letter as source
        if preferred_lower in text_lower:
            idx = text_lower.index(preferred_lower)
            # Check if this letter is already used in this context
            if preferred_lower not in self.context_accelerators[context]:
                text = text[:idx] + "&" + text[idx:]
                self.context_accelerators[context].add(preferred_lower)
                assigned = True
                logging.debug(
                    f"Assigned accelerator '&{text[idx]}' in context '{context}'"
                )

        # Second try: first letter of translation
        if not assigned and text:
            first_letter = text[0].lower()
            if (
                first_letter.isalpha()
                and first_letter not in self.context_accelerators[context]
            ):
                text = "&" + text
                self.context_accelerators[context].add(first_letter)
                assigned = True
                logging.debug(
                    f"Assigned accelerator '&{text[0]}' (first letter) in context '{context}'"
                )

        # Third try: any unused letter
        if not assigned:
            for i, char in enumerate(text):
                if (
                    char.isalpha()
                    and char.lower() not in self.context_accelerators[context]
                ):
                    text = text[:i] + "&" + text[i:]
                    self.context_accelerators[context].add(char.lower())
                    assigned = True
                    logging.debug(
                        f"Assigned accelerator '&{char}' (fallback) in context '{context}'"
                    )
                    break

        # If still not assigned, warn about conflict
        if not assigned and text:
            self.warnings.append(
                f"Could not assign unique accelerator in context '{context}' for text '{text}'. "
                f"Already used: {', '.join(sorted(self.context_accelerators[context]))}"
            )
            # Assign to first letter anyway (will cause conflict)
            text = "&" + text
            if text[1:2].isalpha():
                self.context_accelerators[context].add(text[1].lower())

        # Restore escaped ampersands
        text = text.replace("<QT_AMPAMP/>", "&&")

        return text

    def validate_translation(
        self, source: str, translation: str, context: str
    ) -> List[str]:
        """
        Validate a translation for Qt-specific issues.

        Args:
            source: Original source text
            translation: Translated text
            context: Context name

        Returns:
            List of warning messages
        """
        warnings = []

        # Check placeholder count and order
        source_placeholders = re.findall(r"%(\d+)", source)
        trans_placeholders = re.findall(r"%(\d+)", translation)

        if len(source_placeholders) != len(trans_placeholders):
            warnings.append(
                f"Placeholder count mismatch in '{context}': "
                f"source has {source_placeholders}, translation has {trans_placeholders}"
            )
        elif source_placeholders != trans_placeholders:
            # Check if it's just reordering (which might be OK for some languages)
            if sorted(source_placeholders) == sorted(trans_placeholders):
                warnings.append(
                    f"Placeholders reordered in '{context}': "
                    f"source order {source_placeholders}, translation order {trans_placeholders}"
                )
            else:
                warnings.append(
                    f"Placeholder mismatch in '{context}': "
                    f"source has {source_placeholders}, translation has {trans_placeholders}"
                )

        # Check for suspicious placeholder patterns (like %1 in middle of word)
        suspicious = re.findall(r"\w%\d+\w", translation)
        if suspicious:
            warnings.append(
                f"Suspicious placeholder placement in '{context}': {suspicious}"
            )

        # Check %n placeholder
        source_has_n = "%n" in source
        trans_has_n = "%n" in translation
        if source_has_n != trans_has_n:
            warnings.append(
                f"%n placeholder mismatch in '{context}': "
                f"source {'has' if source_has_n else 'lacks'} %n, "
                f"translation {'has' if trans_has_n else 'lacks'} %n"
            )

        return warnings

    def build_translation_prompt(
        self, text: str, src_lang: str, tgt_lang: str, is_menu_item: bool = False
    ) -> str:
        """
        Build an appropriate translation prompt based on text content.

        Args:
            text: Text to translate (with placeholders already protected)
            src_lang: Source language name
            tgt_lang: Target language name
            is_menu_item: Whether this is a menu item

        Returns:
            Translation prompt
        """
        # Check what special elements are present
        has_placeholders = bool(re.search(r"<QT_P\d+/>|<QT_PN/>|<QT_VAR_\w+/>", text))

        # Build appropriate prompt
        if is_menu_item:
            prompt = f"Translate this menu item from {src_lang} to {tgt_lang}:\n{text}"
        elif has_placeholders:
            # Only mention placeholders if they actually exist
            prompt = (
                f"Translate from {src_lang} to {tgt_lang}. "
                f"Keep all <QT_*> tokens exactly as they appear:\n{text}"
            )
        else:
            # Simple translation, no special handling needed
            prompt = f"Translate from {src_lang} to {tgt_lang}:\n{text}"

        return prompt

    def translate_qt_string(
        self,
        source: str,
        context: str,
        src_lang: str,
        tgt_lang: str,
        translate_func: Callable[[str], str],
        is_menu_item: bool = False,
    ) -> Tuple[str, List[str]]:
        """
        Translate a Qt string with proper handling of Qt-specific elements.

        Args:
            source: Source text to translate
            context: Context name (for accelerator tracking)
            src_lang: Source language name
            tgt_lang: Target language name
            translate_func: Function to perform actual translation (takes text, returns translation)
            is_menu_item: Whether this is a menu item

        Returns:
            Tuple of (translated text, list of warnings)
        """
        if not source or not source.strip():
            return source, []

        # Extract accelerator
        clean_source, accel_letter = self.extract_accelerator(source)

        # Protect placeholders
        protected = self.protect_placeholders(clean_source)

        # Perform translation with protected text
        try:
            # Pass the protected text directly to the translation function
            # The translation service doesn't need to know about our prompt formatting
            translated = translate_func(protected)
        except Exception as e:
            logging.error(f"Translation failed for '{source}': {e}")
            return source, [f"Translation failed: {e}"]

        # Restore placeholders
        translated = self.restore_placeholders(translated)

        # Assign accelerator if needed
        if accel_letter:
            translated = self.assign_accelerator(translated, accel_letter, context)

        # Validate translation
        warnings = self.validate_translation(source, translated, context)

        return translated, warnings

    def reset_context(self, context: str) -> None:
        """
        Reset accelerator tracking for a context.

        Args:
            context: Context name to reset
        """
        self.context_accelerators[context].clear()

    def get_all_warnings(self) -> List[str]:
        """
        Get all accumulated warnings.

        Returns:
            List of warning messages
        """
        return self.warnings.copy()

    def clear_warnings(self) -> None:
        """Clear all accumulated warnings."""
        self.warnings.clear()
