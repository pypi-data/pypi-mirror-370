export interface ContextCommandParams {
  contextCommandGroups: {
    commands: {
      command: string;
    }[];
  }[];
}

export interface FileContext {
  path: string;
}
