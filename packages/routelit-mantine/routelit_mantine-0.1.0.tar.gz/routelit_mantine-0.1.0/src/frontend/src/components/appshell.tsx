import { ComponentProps } from "react";
import { AppShell, Burger, Group, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

interface RLAppShellProps extends ComponentProps<typeof AppShell> {
  title?: string;
  logo?: string;
  navbarProps?: ComponentProps<typeof AppShell.Navbar>;
}

export function RLAppShell({
  children,
  title,
  logo,
  navbarProps,
  ...props
}: React.PropsWithChildren<RLAppShellProps>) {
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure();
  const [desktopOpened, { toggle: toggleDesktop }] = useDisclosure(true);
  title = title ?? "RouteLit";
  logo = logo ?? "/routelit/routelit.svg";
  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: "sm",
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
        ...navbarProps,
      }}
      padding="md"
      {...props}
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger
            opened={mobileOpened}
            onClick={toggleMobile}
            hiddenFrom="sm"
            size="sm"
          />
          <Burger
            opened={desktopOpened}
            onClick={toggleDesktop}
            visibleFrom="sm"
            size="sm"
          />
          <img src={logo} alt="logo" width={30} height={30} />
          <Text fw={700} fz="xl">
            {title}
          </Text>
        </Group>
      </AppShell.Header>
      {children}
    </AppShell>
  );
}
