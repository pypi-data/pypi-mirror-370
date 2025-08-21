const jestJupyterLab = require('@jupyterlab/testutils/lib/jest-config');

const esModules = [
    '@codemirror/',
    '@jupyter/',
    '@microsoft/',
    '@jupyter-lsp/',
    'vscode-languageserver-types',
    '@jupyterlab/',
    'lib0',
    'nanoid',
    'vscode-ws-jsonrpc',
    'y\\-protocols',
    'y\\-websocket',
    'yjs',
    'exenv-es6',
    '',
    'uuid'
].join('|');

const jlabConfig = jestJupyterLab(__dirname);

const {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv,
  setupFiles,
  testPathIgnorePatterns,
  transform
} = jlabConfig;

module.exports = {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv: [...(setupFilesAfterEnv || []), '<rootDir>/src/__tests__/setup.ts'],
  setupFiles,
  transform,
  automock: false,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/.ipynb_checkpoints/*'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['lcov', 'text', 'cobertura'],
  testEnvironment: 'jsdom',
  verbose: true,
  globals: {
    'navigator': {
      userAgent: 'node.js'
    },
    'window': {
      location: {
        href: 'http://localhost'
      }
    }
  },
  testRegex: 'src/.*/.*.spec.ts[x]?$',
  testPathIgnorePatterns: [
      ...testPathIgnorePatterns,
      '/dist/'
  ],
  transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`
],
  transform: {
    '^.+\\.[t|j]sx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '\\.svg$': '<rootDir>/src/__tests__/__mocks__/filemock.ts',
  },
};