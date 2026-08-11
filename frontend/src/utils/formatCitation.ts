/**
 * Converts a source file and chunk ID into a clean display format.
 * Example:
 * input: "02_employment_agreement_excerpt.md", "02_employment_agreement_excerpt.md::notice_period"
 * output: "Exh. 02 § notice_period"
 */
export function formatCitation(sourceFile: string, chunkId: string): string {
  // Extract document number if it exists (e.g., "02")
  const match = sourceFile.match(/^(\d+)_/);
  const docNum = match ? match[1] : '?';

  // Extract the section name after the '::'
  const parts = chunkId.split('::');
  const section = parts.length > 1 ? parts[parts.length - 1] : 'unknown';

  return `Exh. ${docNum} § ${section}`;
}
