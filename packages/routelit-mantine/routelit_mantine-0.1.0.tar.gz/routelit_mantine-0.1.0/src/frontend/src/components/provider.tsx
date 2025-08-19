import { MantineProvider, MantineProviderProps, createTheme } from "@mantine/core";


type ProviderProps = MantineProviderProps & {
  theme: Partial<Parameters<typeof createTheme>[0]>;
};

export function RLProvider({ children, theme, ...props }: ProviderProps) {
  const _theme = createTheme(theme);
  return <MantineProvider theme={_theme} {...props}>{children}</MantineProvider>;
}
