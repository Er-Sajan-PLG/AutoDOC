// Browser-side example: use relative URLs, including behind a preview/reverse proxy.
export async function listTasks() {
  const response = await fetch('/tasks');
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
