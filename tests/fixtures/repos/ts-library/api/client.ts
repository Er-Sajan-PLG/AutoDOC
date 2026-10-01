// A typed client surface: a public API, but not an HTTP contract.
export function connect(baseUrl: string): Client {
  return new Client(baseUrl);
}
