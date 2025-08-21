import { MantineProvider, AppShell, Group, Container, Flex, Grid, GridCol, SimpleGrid, Text } from "@mantine/core";

function App() {
  return (
    <MantineProvider>
      <AppShell>
        <AppShell.Navbar>
          <h2>Sidebar</h2>
          <p>This is the sidebar content</p>
          <h2>Group</h2>
          <Group>
            <button>Click me 1</button>
            <button>Click me 2</button>
            <button>Click me 3</button>
          </Group>
        </AppShell.Navbar>
        <AppShell.Main>
          <h2>Group</h2>
          <Group>
            <Text>Hello</Text>
            <Text>World</Text>
          </Group>
          <h2>Container</h2>
          <Container>
            <h2>Flex</h2>
            <Flex
              direction={{ base: "column", sm: "row" }}
              gap={{ base: "sm", sm: "lg" }}
              justify={{ sm: "center" }}
            >
              <Text>Hello</Text>
              <Text>World</Text>
            </Flex>
          </Container>
          <h2>Grid</h2>
          <Grid>
            <GridCol span={6}>
              <Text>Hello</Text>
            </GridCol>
            <GridCol span={3}>
              <Text>Hello</Text>
            </GridCol>
            <GridCol span={3}>
              <Text>Hello</Text>
            </GridCol>
            <GridCol span={3}>
              <Text>Hello</Text>
            </GridCol>
            <GridCol span={3}>
              <Text>Hello</Text>
            </GridCol>
            <GridCol span={6}>
              <Text>Hello</Text>
            </GridCol>
          </Grid>
          <Grid>
            <GridCol span={4}>1</GridCol>
            <GridCol span={4}>2</GridCol>
            <GridCol span={4}>3</GridCol>
            <GridCol span={4}>4</GridCol>
            <GridCol span={4}>5</GridCol>
          </Grid>
          <h2>SimpleGrid</h2>
          <SimpleGrid cols={3}>
            <button>1</button>
            <button>2</button>
            <button>3</button>
            <button>4</button>
            <button>5</button>
            <button>6</button>
            <button>7</button>
            <button>8</button>
            <button>9</button>
          </SimpleGrid>
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}

export default App;
