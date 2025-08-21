from datetime import date, datetime, time, timedelta

from flask import Flask, Response
from routelit import RouteLit
from routelit_flask import RouteLitFlaskAdapter

from routelit_mantine import RLBuilder, create_drawer_decorator

app = Flask(__name__)

rl = RouteLit(BuilderClass=RLBuilder)
routelit_adapter = RouteLitFlaskAdapter(
    rl,
    ### TO USE LOCAL VITE DEV SERVER, UNCOMMENT THE FOLLOWING LINES
    run_mode="dev_components",
    local_components_server="http://localhost:5173",
).configure(app)

drawer = create_drawer_decorator(rl)


@rl.fragment("checkboxes")
def checkboxes_fragment(ui: RLBuilder) -> None:
    ui.header("Checkbox")
    if ui.checkbox(label="Checkbox 0", checked=True, on_change=lambda checked: print(f"Checkbox checked: {checked}")):
        ui.text("Checkbox checked")
    else:
        ui.text("Checkbox not checked")
    # Example with description and custom color
    if ui.checkbox(
        label="Checkbox with description", description="This is a helpful description", color="red", checked=False
    ):
        ui.text("Description checkbox checked")

    # Example with different size and radius
    if ui.checkbox(label="Large rounded checkbox", size="lg", radius="xl", checked=False):
        ui.text("Large checkbox checked")

    # Example with error state
    if ui.checkbox(label="Checkbox with error", error="This field has an error", checked=False):
        ui.text("Error checkbox checked")

    # Example with label position and disabled state
    if ui.checkbox(label="Left-aligned disabled checkbox", label_position="left", disabled=True, checked=True):
        ui.text("Disabled checkbox checked")

    # Example with auto_control and custom name
    if ui.checkbox(label="Auto-contrast checkbox", auto_contrast=True, checked=False):
        ui.text("Auto-contrast checkbox checked")


@rl.fragment("chips")
def chip_fragment(ui: RLBuilder) -> None:
    ui.header("Chip")
    if ui.chip(
        label="Chip 0", checked=True, on_change=lambda checked: print(f"Chip checked: {checked}"), icon=ui.icon("home")
    ):
        ui.text("Chip checked")
    else:
        ui.text("Chip not checked")

    countries = {
        "US": "United States",
        "CA": "Canada",
        "UK": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
    }
    country_selected = ui.chip_group(
        key="countries_chipgroup",
        options=list(countries.keys()),
        multiple=False,
        on_change=lambda value: print(f"Chip group value changed to {value}"),
    )
    ui.text(f"Country selected: {country_selected}")
    languages = {
        "en": "English",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
    }
    language_selected = ui.chip_group(
        key="languages_chipgroup",
        options=list(languages.keys()) + [{"label": "All", "value": "all", "color": "red"}],  # noqa: RUF005
        multiple=True,
        format_func=lambda value: languages.get(value, value),
        on_change=lambda value: print(f"Chip group value changed to {value}"),
    )
    ui.text(f"Language selected: {language_selected}")


@rl.fragment("inputs")
def inputs_fragment(ui: RLBuilder) -> None:
    with ui.fieldset(legend="Input fields", radius="sm"):
        if ui.checkbox(
            label="Checkbox 0", checked=True, on_change=lambda checked: print(f"Checkbox checked: {checked}")
        ):
            ui.text("Checkbox checked")

        checkbox_group = ui.checkbox_group(
            label="Checkbox group",
            description="This is a description",
            options=[
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
                {"label": "Option 3", "value": "option3"},
            ],
            value=["option1", "option2"],
            on_change=lambda value: print(f"Checkbox group value changed to {value}"),
        )
        ui.text(f"Checkbox group: {checkbox_group}")

        color = ui.color_input(
            label="Color", value="#000000", on_change=lambda value: print(f"Color changed to {value}")
        )
        ui.text(f"Color: {color}")

        text_input = ui.text_input(
            label="Text input",
            value="Hello",
            on_change=lambda value: print(f"Text input changed to {value}"),
            description="This is a description",
            left_section=ui.icon("homeFilled", size=16),
            right_section=ui.icon("ChevronRightPipe", size=16),
        )
        ui.text(f"Text input: {text_input}")
        native_select = ui.native_select(
            label="Native select",
            description="This is a description",
            options=[
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
                {"label": "Option 3", "value": "option3"},
            ],
            value="option1",
            on_change=lambda value: print(f"Native select changed to {value}"),
            left_section=ui.icon("homeFilled", size=16),
            right_section=ui.icon("ArrowBigDown", size=16),
        )
        ui.text(f"Native select: {native_select}")
        number_input = ui.number_input(
            label="Number input",
            value=10,
            on_change=lambda value: print(f"Number input changed to {value}"),
            left_section=ui.icon("coin"),
        )
        ui.text(f"Number input: {number_input}")

        password_input = ui.password_input(
            label="Password input",
            value="Hello",
            on_change=lambda value: print(f"Password input changed to {value}"),
        )
        ui.text(f"Password input: {password_input}")

        radio_group = ui.radio_group(
            label="Radio group",
            options=[
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
                {"label": "Option 3", "value": "option3"},
            ],
            value="option1",
            on_change=lambda value: print(f"Radio group value changed to {value}"),
        )
        ui.text(f"Radio group: {radio_group}")

        range_slider = ui.range_slider(
            label="Range slider",
            description="This is a description",
            value=(25, 75),
            min_value=0,
            max_value=100,
            step=1,
            marks=[{"label": "Label 25", "value": 25}, {"label": "Label 50", "value": 50}],
            # label_always_on=True,
            on_change=lambda value: print(f"Range slider value changed to {value}"),
        )
        ui.text(f"Range slider: {range_slider}")

        with ui.stack():
            ui.text("Rating")
            rating = ui.rating(
                "rating0",
                value=3,
                on_change=lambda value: print(f"Rating value changed to {value}"),
                count=5,
                fractions=2,
                read_only=False,
                size="lg",
                color="red",
            )
            ui.text(f"Rating: {rating}")

        fruit = ui.segmented_control(
            "segmentedcontrol0",
            options=[{"label": "Apple", "value": "apple"}, "Banana", "Cherry", {"label": "All", "value": "all"}],
            # value="Banana",
            on_change=lambda value: print(f"Segmented control value changed to {value}"),
        )
        ui.text(f"Fruit: {fruit}")

        slider = ui.slider(
            label="Slider",
            value=50,
            min_value=0,
            max_value=100,
            step=1,
            marks=[{"label": "Label 25", "value": 25}, {"label": "Label 50", "value": 50}],
            # restrict_to_marks=True,
            # show_label_on_hover=True,
            # thumb_size="lg",
            on_change=lambda value: print(f"Slider value changed to {value}"),
        )
        ui.text(f"Slider: {slider}")

        is_dark = ui.switch(
            label="Is dark",
            value=True,
            key="is_dark_switch",
            on_change=lambda value: print(f"Is dark value changed to {value}"),
            thumb_icon=ui.icon("Moon") if not ui.session_state.get("is_dark_switch", False) else ui.icon("Sun"),
        )
        ui.text(f"Is dark: {is_dark}")

        switch_group = ui.switch_group(
            label="Switch group",
            description="This is a description",
            options=[
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
                {"label": "Option 3", "value": "option3", "color": "red", "size": "lg"},
                "Option 4",
            ],
            value=["option1", "option2"],
            # group_props={"direction": "column"},
            on_change=lambda value: print(f"Switch group value changed to {value}"),
        )
        ui.text(f"Switch group: {switch_group}")
        bio = ui.textarea(
            label="Bio",
            value="Hello",
            on_change=lambda value: print(f"Bio value changed to {value}"),
        )
        ui.text(f"Bio: {bio}")


@rl.fragment("combobox")
def combobox_fragment(ui: RLBuilder) -> None:
    ui.header("Autocomplete")
    fruit = ui.autocomplete(
        label="Autocomplete",
        description="This is a description",
        # value="Hello",
        data=[
            # {"group": "Tropical", "options": ["Banana", "Pineapple", "Watermelon"]},
            "Apple",
            "Cherry",
            "Orange",
            "Pear",
            "Strawberry",
            "Watermelon",
        ],
        left_section=ui.icon("Home", size=16),
        right_section=ui.icon("ChevronRightPipe", size=16),
        on_change=lambda value: print(f"Autocomplete value changed to {value}"),
    )
    ui.text(f"Fruit: {fruit}")

    ui.header("multiselect")
    cities = {
        "SD": "Santo Domingo",
        "LA": "La Altagracia",
        "BA": "Barahona",
        "SA": "Santiago",
        "SM": "Samaná",
        "PU": "Puerto Plata",
    }
    cities_selected = ui.multiselect(
        "DR City",
        list(cities.keys()),
        searchable=True,
        description="Select a city of the DR you want to go",
        format_func=lambda x: cities.get(x, x),
        left_section=ui.icon("Home", size=16),
        right_section=ui.icon("ChevronRightPipe", size=16),
    )
    ui.text(f"Selected cities {cities_selected}")

    hobbies = {
        "sw": "Swimming",
    }
    hobbie = ui.select(
        "Hobbie",
        ["sw", "Reading", "Writing", "Coding", "Gaming", "Other", {"label": "All", "value": "all"}],
        searchable=True,
        value="sw",
        description="Select a hobbie",
        format_func=lambda x: hobbies.get(x, x),
        left_section=ui.icon("Home", size=16),
        right_section=ui.icon("ChevronRightPipe", size=16),
    )
    ui.text(f"Hobbie: {hobbie}")

    js_frameworks = {
        "react": "React",
        "vue": "Vue",
        "angular": "Angular",
        "svelte": "Svelte",
        "solid": "Solid",
    }
    js_frameworks_selected = ui.tags_input(
        "JS Frameworks",
        list(js_frameworks.values()),
        description="Select a JS framework",
        max_tags=3,
        value=["ember"],
        on_change=lambda value: print(f"Tags input value changed to {value}"),
        left_section=ui.icon("Home", size=16),
        right_section=ui.icon("ChevronRightPipe", size=16),
    )
    ui.text(f"JS Frameworks: {js_frameworks_selected}")


@rl.fragment("buttons")
def buttons_fragment(ui: RLBuilder) -> None:  # noqa: C901
    ui.header("Buttons")
    if ui.button("Click me a", on_click=lambda: print("Hello")):
        ui.text("Hello")
    if ui.action_icon("homeFilled"):
        ui.text("Home pressed")
    if ui.button("Click me b", on_click=lambda: print("Hello")):
        ui.text("Hello")

    with ui.action_icon_group(orientation="horizontal"):
        if ui.action_icon("ChevronDown", variant="default", rl_virtual=True):
            ui.session_state["counter"] = ui.session_state.get("counter", 0) - 1
        ui.action_icon_group_section(
            text=f"Hello {ui.session_state.get('counter', 0)}",
            variant="default",
            bg="var(--mantine-color-body)",
            miw=60,
        )
        if ui.action_icon("ChevronUp", variant="default", rl_virtual=True):
            ui.session_state["counter"] = ui.session_state.get("counter", 0) + 1
            ui.rerun()

    if ui.button("Click full width", on_click=lambda: print("Hello"), full_width=True):
        ui.text("Hello full width")

    if ui.button("Click lg", on_click=lambda: print("Hello"), size="lg"):
        ui.text("Hello lg")

    if ui.button(
        "Click gradient", on_click=lambda: print("Hello"), gradient={"from": "blue", "to": "cyan"}, variant="gradient"
    ):
        ui.text("Hello gradient")

    if ui.button("Click loading", on_click=lambda: print("Hello"), loading=True):
        ui.text("Hello loading")

    if ui.button("Click disabled", on_click=lambda: print("Hello"), disabled=True):
        ui.text("Hello disabled")

    if ui.button("Click radius", on_click=lambda: print("Hello"), radius="xl"):
        ui.text("Hello radius")

    if ui.button(
        "Click size",
        on_click=lambda: print("Hello"),
        size="md",
        left_section=ui.icon("homeFilled", size=16),
        right_section=ui.icon("ChevronRightPipe", size=16),
    ):
        ui.text("Hello size")

    if ui.button("Click variant", on_click=lambda: print("Hello"), variant="outline"):
        ui.text("Hello variant")


@rl.fragment("layouts")
def layouts_fragment(ui: RLBuilder) -> None:
    ui.header("Container")
    with ui.container(fluid=True, size="xl", bg="var(--mantine-color-blue-light)"):
        ui.text("Hello World")

    ui.header("Flex")
    with ui.flex(direction="row", gap="md", justify="space-between", bg="var(--mantine-color-blue-light)"):
        ui.text("Flex Hello World 1")
        ui.text("Flex Hello World 2")
        ui.text("Flex Hello World 3")
        ui.text("Flex Hello World 4")

    ui.header("Grid")
    with ui.grid(
        columns=4,
        gutter={"xs": 10, "sm": 20, "md": 30, "lg": 40, "xl": 50},
        breakpoints={
            "xs": 12,
            "sm": 12,
            "md": 12,
            "lg": 12,
            "xl": 12,
        },
    ):
        with ui.grid_col(span=1):
            ui.text("Grid Hello World 1")
        with ui.grid_col(span=1):
            ui.text("Grid Hello World 2")
        with ui.grid_col(span=1):
            ui.text("Grid Hello World 3")

    ui.header("Group")
    with ui.group(align="center", gap="md", justify="space-between", bg="var(--mantine-color-blue-light)"):
        ui.text("Group Hello World 1")
        ui.text("Group Hello World 2")
        ui.text("Group Hello World 3")
        ui.text("Group Hello World 4")

    ui.header("SimpleGrid")
    with ui.simple_grid(
        cols=4, spacing="md", type="container", vertical_spacing="md", bg="var(--mantine-color-blue-light)"
    ):
        ui.text("SimpleGrid Hello World 1")
        ui.text("SimpleGrid Hello World 2")
        ui.text("SimpleGrid Hello World 3")
        ui.text("SimpleGrid Hello World 4")

    ui.header("Space")
    with ui.flex(direction="row", gap="md", bg="var(--mantine-color-blue-light)"):
        ui.text("Space Hello World 1")
        ui.space()
        ui.text("Space Hello World 3")
        ui.space(w="xl")
        ui.text("Space Hello World 4")

    ui.header("Stack")
    with ui.stack(align="center", gap="md", justify="space-between", bg="var(--mantine-color-blue-light)"):
        ui.text("Stack Hello World 1")
        ui.text("Stack Hello World 2")
        ui.text("Stack Hello World 3")
        ui.text("Stack Hello World 4")


def navigation_fragment(ui: RLBuilder) -> None:
    ui.anchor(
        href="/",
        text="Home",
        # is_external=True,
        variant="gradient",
        gradient={"from": "blue", "to": "red"},
    )
    ui.nav_link(
        href="/",
        label="Home",
        # is_external=True,
        variant="gradient",
        gradient={"from": "blue", "to": "red"},
    )
    tab1, tab2, tab3, tab4 = ui.tabs(
        tabs=[
            ui.tab(value="tab1", label="Home", left_section=ui.icon("Home", size=16)),
            ui.tab(value="tab2", label="Tab 2", right_section=ui.icon("ChevronRightPipe", size=16)),
            "🏠 Tab 4",
            ui.tab(value="tab3", label="Tab 3", ml="auto"),
        ],
        default_value="tab3",
        variant="outline",
    )
    with tab1:
        ui.text("Tab 1")
    with tab2:
        ui.text("Tab 2")
    with tab3:
        ui.text("Tab 3")
    with tab4:
        ui.text("Tab 4")


@rl.fragment("sidebar_fragment")
def sidebar_fragment(ui: RLBuilder) -> None:
    if ui.button("Click me", on_click=lambda: print("Hello")):
        ui.text("Hello")
    ui.nav_link(
        href="#",
        label="Home",
        is_external=True,
        variant="gradient",
        gradient={"from": "blue", "to": "red"},
        left_section=ui.icon("Home", size=16),
    )


def navigation_sidebar(ui: RLBuilder) -> None:
    with ui.sidebar:
        ui.subheader("Sidebar")
        sidebar_fragment(ui)


@rl.fragment("feedback")
def feedback_fragment(ui: RLBuilder) -> None:
    if ui.button("show alert", on_click=lambda: print("Close")):
        ui.alert("Alert title", text="Text inline", color="red", radius="xl", icon=ui.icon("AlertCircle"))
        with ui.alert("Alert title 2", color="red", radius="xl", icon=ui.icon("AlertCircle")):
            ui.text("Hello as child")

    if "should_show_alert" not in ui.session_state:
        ui.session_state["should_show_alert"] = True

    def set_should_show_alert(value: bool) -> None:
        ui.session_state["should_show_alert"] = value

    print("should_show_alert", ui.session_state["should_show_alert"])
    ui.checkbox("Show alert", checked=ui.session_state["should_show_alert"], on_change=set_should_show_alert)
    if ui.session_state["should_show_alert"]:
        with ui.alert(
            "Alert title 2 as child",
            color="red",
            radius="xl",
            icon=ui.icon("AlertCircle"),
            on_close=lambda: set_should_show_alert(False),
            with_close_button=True,
            close_button_label="Close",
        ):
            ui.text("Hello 2 as child")

        ui.alert(
            "Alert title 3 as child",
            text="Text inline",
            color="red",
            radius="xl",
            icon=ui.icon("AlertCircle"),
            with_close_button=True,
        )

    if ui.checkbox("Show notification with close button", checked=True):
        ui.notification(
            "Notification 3",
            text="Text inline",
            color="red",
            radius="xl",
            icon=ui.icon("AlertCircle", size=16),
            with_close_button=True,
            close_button_label="Close",
        )
        with ui.notification(
            "Notification 4",
            color="green",
            radius="xl",
            icon=ui.icon("AlertCircle", size=16),
            with_close_button=True,
            close_button_label="Close",
        ):
            ui.text("Notification body as child")

    if "progress" not in ui.session_state:
        ui.session_state["progress"] = 0
    ui.progress(
        value=ui.session_state["progress"], color="red", radius="xl", size="lg", striped=True, transition_duration=500
    )
    if ui.button("Increment progress", left_section=ui.icon("ArrowUp", size=16)):
        ui.session_state["progress"] += 10
        if ui.session_state["progress"] > 100:
            ui.session_state["progress"] = 0
        ui.rerun()


@rl.dialog("dialog_example", title="Dialog title by RGT")
def dialog_example(ui: RLBuilder) -> None:
    ui.text("Hello 1")
    ui.markdown("""
    # Hello 1
    This is a dialog
    """)
    if "counter" not in ui.session_state:
        ui.session_state["counter"] = 0
    if ui.button("Increment counter", on_click=lambda: print("Increment counter")):
        ui.session_state["counter"] += 1
        # ui.rerun()
    ui.text(f"Counter: {ui.session_state['counter']}")
    if ui.button("close dialog", on_click=lambda: print("Close dialog")):
        ui.rerun(scope="app")


@drawer("example_drawer", title="Drawer title", offset=8, radius="md", with_close_button=True)
def example_drawer(ui: RLBuilder) -> None:
    ui.text("This is a drawer!")
    ui.text("Built using the generic overlay decorator system")

    if ui.button("Close Drawer"):
        ui.rerun(scope="app")
    if "counter" not in ui.session_state:
        ui.session_state["counter"] = 0
    if ui.button("Increment counter", on_click=lambda: print("Increment counter")):
        ui.session_state["counter"] += 1
    ui.text(f"Counter: {ui.session_state['counter']}")


@rl.fragment("overlays")
def overlays_fragment(ui: RLBuilder) -> None:  # noqa: C901
    is_dialog_open = ui.button("show dialog")
    print("is_dialog_open", is_dialog_open)

    if "overlay_counter" not in ui.session_state:
        ui.session_state["overlay_counter"] = 0
    if ui.button("Increment overlay counter", on_click=lambda: print("Increment overlay counter")):
        ui.session_state["overlay_counter"] += 1
    ui.text(f"Overlay counter: {ui.session_state['overlay_counter']}")

    if is_dialog_open:
        dialog_example(ui)

    nested_fragment(ui)

    if "should_show_drawer" not in ui.session_state:
        ui.session_state["should_show_drawer"] = False
    if ui.button("show drawer 1", on_click=lambda: print("show drawer 1")):
        example_drawer(ui)
    if ui.button("show drawer 2", on_click=lambda: print("show drawer 2")):
        ui.session_state["should_show_drawer"] = True

    def on_close_drawer() -> None:
        ui.session_state["should_show_drawer"] = False

    if ui.session_state["should_show_drawer"]:
        with ui.drawer(
            title="Drawer title with on_close",
            offset=8,
            radius="md",
            close_on_escape=True,
            close_on_click_outside=True,
            on_close=on_close_drawer,
            with_close_button=True,
            close_button_props={"aria-label": "Close drawer"},
        ):
            ui.text("Drawer content")
            ui.text("Drawer content 2")
            with ui.flex(direction="row", gap="md"):
                ui.text("Hello 5")
                ui.text("Hello 6")
                ui.text("Hello 7")
                ui.text("Hello 8")
            if "counter" not in ui.session_state:
                ui.session_state["counter"] = 0
            if ui.button("Increment counter", on_click=lambda: print("Increment counter")):
                ui.session_state["counter"] += 1
            ui.text(f"Counter: {ui.session_state['counter']}")

    if "should_show_dialog" not in ui.session_state:
        ui.session_state["should_show_dialog"] = False
    if ui.button("show dialog 1", on_click=lambda: print("show dialog 1")):
        ui.session_state["should_show_dialog"] = True

    def on_close_dialog() -> None:
        ui.session_state["should_show_dialog"] = False

    if ui.session_state["should_show_dialog"]:
        with ui.dialog(
            title="Dialog title",
            on_close=on_close_dialog,
            with_close_button=True,
            close_button_props={"aria-label": "Close dialog"},
        ):
            ui.text("Dialog content")
            ui.text("Dialog content 2")
            with ui.flex(direction="row", gap="md"):
                ui.text("Hello 5")
                ui.text("Hello 6")
                ui.text("Hello 7")
            if "counter" not in ui.session_state:
                ui.session_state["counter"] = 0
            if ui.button("increment counter", on_click=lambda: print("increment counter"), rl_virtual=True):
                ui.session_state["counter"] += 1
            ui.text(f"Counter: {ui.session_state['counter']}")

    with ui.affix(m="sm"):
        if ui.button("Hello affix", on_click=lambda: print("Hello affix")):
            ui.text("Hello affix")

    # ui.text("Hello after dialog")


@rl.fragment("nested_fragment")
def nested_fragment(ui: RLBuilder) -> None:
    ui.text("Hello 1")
    ui.text("Hello 2")
    ui.text("Hello 3")
    ui.text("Hello 4")
    if ui.checkbox("Show hidden text", checked=True):
        ui.text("Hidden text")

    with ui.flex(direction="row", gap="md"):
        ui.text("Hello 5")
        ui.text("Hello 6")
        ui.text("Hello 7")
        ui.text("Hello 8")


@rl.fragment("sidebar_view")
def sidebar_view(ui: RLBuilder) -> None:
    ui.set_provider_props(theme={"primaryColor": "green"})
    ui.set_app_shell_props(title="Mantine RouteLit", navbar_props={"width": 200})
    with ui.scroll_area():
        ui.nav_link(
            href="/",
            label="Home",
            left_section=ui.icon("Home"),
            exact=True,
        )
        ui.nav_link(
            href="/layouts",
            label="Layouts",
            left_section=ui.icon("Layout"),
        )
        ui.nav_link(
            href="/checkboxes",
            label="Checkboxes",
            left_section=ui.icon("Checkbox"),
        )
        ui.nav_link(
            href="/chips",
            label="Chips",
            left_section=ui.icon("Label"),
        )
        ui.nav_link(
            href="/inputs",
            label="Inputs",
            left_section=ui.icon("Forms"),
        )
        ui.nav_link(
            href="/combobox",
            label="Combobox",
            left_section=ui.icon("Select"),
        )
        ui.nav_link(
            href="/buttons",
            label="Buttons",
            left_section=ui.icon("CircuitPushbutton"),
        )
        ui.nav_link(
            href="/navigation",
            label="Navigation",
            left_section=ui.icon("Navigation"),
        )
        ui.nav_link(
            href="/feedback",
            label="Feedback",
            left_section=ui.icon("ExclamationCircle"),
        )
        ui.nav_link(
            href="/overlays",
            label="Overlays",
            left_section=ui.icon("ImageInPicture"),
        )
        ui.nav_link(
            href="/data_display",
            label="Data Display",
            left_section=ui.icon("Database"),
        )
        ui.nav_link(
            href="/miscellaneous",
            label="Miscellaneous",
            left_section=ui.icon("Tools"),
        )
        ui.nav_link(
            href="/dates",
            label="Dates",
            left_section=ui.icon("Calendar"),
        )
        with ui.nav_link(
            href="#",
            label="Charts",
            is_external=True,
            left_section=ui.icon("Graph"),
        ):
            ui.nav_link(
                href="/area_chart",
                label="Area Chart",
                left_section=ui.icon("ChartArea"),
            )
            ui.nav_link(
                href="/bar_chart",
                label="Bar Chart",
                left_section=ui.icon("ChartBar"),
            )
            ui.nav_link(
                href="/line_chart",
                label="Line Chart",
                left_section=ui.icon("ChartLine"),
            )
            ui.nav_link(
                href="/composite_chart",
                label="Composite Chart",
                left_section=ui.icon("ChartAreaLine"),
            )
            ui.nav_link(
                href="/donut_chart",
                label="Donut Chart",
                left_section=ui.icon("ChartDonut"),
            )
            ui.nav_link(
                href="/funnel_chart",
                label="Funnel Chart",
                left_section=ui.icon("ChartFunnel"),
            )
            ui.nav_link(
                href="/pie_chart",
                label="Pie Chart",
                left_section=ui.icon("ChartPie"),
            )
            ui.nav_link(
                href="/radar_chart",
                label="Radar Chart",
                left_section=ui.icon("ChartRadar"),
            )
            ui.nav_link(
                href="/scatter_chart",
                label="Scatter Chart",
                left_section=ui.icon("ChartScatter"),
            )
            ui.nav_link(
                href="/bubble_chart",
                label="Bubble Chart",
                left_section=ui.icon("ChartBubble"),
            )
            ui.nav_link(
                href="/radial_bar_chart",
                label="Radial Bar Chart",
                left_section=ui.icon("ChartArcs"),
            )
            ui.nav_link(
                href="/sparkline_chart",
                label="Sparkline Chart",
                left_section=ui.icon("ChartLine"),
            )
            ui.nav_link(
                href="/heatmap",
                label="Heatmap",
                left_section=ui.icon("Matrix"),
            )
        with ui.nav_link(
            href="#",
            label="Search Engines",
            is_external=True,
            variant="gradient",
            gradient={"from": "blue", "to": "red"},
            left_section=ui.icon("ListSearch"),
            default_opened=False,
        ):
            # region search engines
            ui.nav_link(
                href="https://www.google.com",
                label="Google",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
                left_section=ui.icon("BrandGoogle"),
            )
            ui.nav_link(
                href="https://www.bing.com",
                label="Bing",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
                right_section=ui.icon("ChevronRightPipe"),
            )
            ui.nav_link(
                href="https://www.duckduckgo.com",
                label="DuckDuckGo",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
            )
            ui.nav_link(
                href="https://www.yahoo.com",
                label="Yahoo",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
            )
            ui.nav_link(
                href="https://www.ask.com",
                label="Ask",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
            )
            ui.nav_link(
                href="https://www.aol.com",
                label="AOL",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
            )
            ui.nav_link(
                href="https://www.ask.com",
                label="Ask",
                is_external=True,
                variant="gradient",
                gradient={"from": "blue", "to": "red"},
            )
            # endregion search engines
        ui.nav_link("#", label="About", left_section=ui.icon("InfoCircle"))


def index_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Home")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Mantine RouteLit")
    ui.markdown("""
    # Mantine RouteLit
    This is a demo of the Mantine RouteLit library.
    """)


def layouts_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Layouts")
    with ui.sidebar:
        sidebar_view(ui)
    layouts_fragment(ui)


def checkboxes_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Checkboxes")
    with ui.sidebar:
        sidebar_view(ui)
    checkboxes_fragment(ui)


def chips_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Chips")
    with ui.sidebar:
        sidebar_view(ui)
    chip_fragment(ui)


def combobox_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Combobox")
    with ui.sidebar:
        sidebar_view(ui)
    combobox_fragment(ui)


def buttons_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Buttons")
    with ui.sidebar:
        sidebar_view(ui)
    buttons_fragment(ui)


def navigation_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Navigation")
    with ui.sidebar:
        sidebar_view(ui)
    navigation_fragment(ui)


def feedback_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Feedback")
    with ui.sidebar:
        sidebar_view(ui)
    feedback_fragment(ui)


def overlays_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Overlays")
    with ui.sidebar:
        sidebar_view(ui)
    overlays_fragment(ui)


def inputs_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Inputs")
    with ui.sidebar:
        sidebar_view(ui)
    inputs_fragment(ui)


def data_display_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Data Display")
    with ui.sidebar:
        sidebar_view(ui)
    ui.header("Data Display")

    ui.header("Accordion")
    variant = ui.select(
        label="Variant",
        options=[
            {"label": "Default", "value": "default"},
            {"label": "Filled", "value": "filled"},
            {"label": "Separated", "value": "separated"},
            {"label": "Contained", "value": "contained"},
            {"label": "Unstyled", "value": "unstyled"},
        ],
        value="default",
    )

    with ui.accordion(variant=variant, chevron=ui.icon("ChevronDown"), chevron_position="left"):
        with ui.accordion_item(label="Accordion item 1", icon=ui.icon("Apple")):
            ui.text("Accordion Body item 1")
        with ui.accordion_item(label="Accordion item 2", chevron=ui.icon("IconCaretDown")):
            ui.text("Accordion Body item 2")
        with ui.accordion_item(label="Accordion item 3"):
            ui.text("Accordion Body item 3")

    ui.hr()
    with ui.accordion(multiple=True, variant=variant):
        with ui.accordion_item(label="Accordion item 1", icon=ui.icon("IconAvocado")):
            ui.text("Accordion Body item 1")
        with ui.accordion_item(label="Accordion item 2", chevron=ui.icon("IconArrowDown")):
            ui.text("Accordion Body item 2")
        with ui.accordion_item(label="Accordion item 3"):
            ui.text("Accordion Body item 3")

    ui.hr()

    with ui.expander(title="Expander 1", chevron=ui.icon("IconArrowDown"), chevron_position="left", variant="unstyled"):
        ui.text("Expander Body 1")

    with ui.expander(title="Expander 2", is_open=True, icon=ui.icon("IconStar"), variant="filled"):
        ui.text("Expander Body 2")
    ui.hr()

    ui.image(src="https://placehold.co/600x400")
    ui.number_formatter(
        value=1000.5,
        prefix="$",
        thousandsGroupStyle="thousand",
        thousandSeparator=",",
        decimalSeparator=".",
        decimalScale=2,
        fixedDecimalScale=True,
    )
    ui.number_formatter(
        value=100 / 3,
        suffix="%",
        decimalSeparator=".",
        decimalScale=2,
        fixedDecimalScale=True,
    )
    with ui.spoiler(max_height=200):
        ui.markdown("""
# Spoiler

This is a spoiler with a lot of text.

Porque de tal manera amó Dios al mundo, que me dio a su Hijo, para que todo aquel que en él cree, no se pierda, sino que tenga vida eterna.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """)

    table_caption = "Table caption"
    table_head = ["Header 1", "Header 2", "Header 3"]
    table_body = [[f"Cell {i * 3 + j + 1}" for j in range(3)] for i in range(10)]
    table_foot = ["Footer 1", "Footer 2", "Footer 3"]
    ui.table(body=table_body, caption=table_caption, head=table_head, foot=table_foot)

    ui.title("Table with builder", order=4)
    with ui.table_scroll_container(max_height=200), ui.table(sticky_header=True):
        with ui.table_head(), ui.table_row():
            for header in table_head:
                ui.table_header(header)
        with ui.table_body():
            for row in table_body:
                with ui.table_row():
                    for cell in row:
                        ui.table_cell(cell)
        with ui.table_foot(), ui.table_row():
            for cell in table_foot:
                ui.table_header(cell)


def miscellaneous_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Miscellaneous")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Miscellaneous")
    with ui.box(p="md"):
        ui.text("Hello in box")
    with ui.paper(withBorder=True, p="md", shadow="sm"):
        ui.text("Hello in paper")
    with ui.scroll_area(type="always", h=200):
        ui.text("Hello in scroll area")
        ui.markdown("""
# Scroll area

This is a scroll area with a lot of text.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """)


def dates_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Dates")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Dates")
    # date_picker = ui.date_picker(label="Date picker")
    # ui.text(f"Date picker: {date_picker}")
    ui.header("Date time picker")
    with ui.group():
        with ui.container():
            date_time_picker = ui.date_time_picker(label="Date time picker", next_icon=ui.icon("ArrowRight"))
            ui.text(f"Date time picker: {date_time_picker}")
            ui.text(f"Date time picker year: {date_time_picker.year if date_time_picker else 'None'}")
            ui.text(f"Date time picker month: {date_time_picker.month if date_time_picker else 'None'}")
            ui.text(f"Date time picker day: {date_time_picker.day if date_time_picker else 'None'}")
            ui.text(f"Date time picker hour: {date_time_picker.hour if date_time_picker else 'None'}")
            ui.text(f"Date time picker minute: {date_time_picker.minute if date_time_picker else 'None'}")
        with ui.container():
            date_time2 = ui.date_time_picker(
                label="Date time picker 2", value=datetime.now(), left_section=ui.icon("Calendar")
            )
            ui.text(f"Date time picker 2: {date_time2}")
            # ui.time_input(label="Time input")

    ui.header("Date picker")
    with ui.group():
        with ui.container():
            date0 = ui.date_picker(label="Date picker", value=date.today())
            ui.text(f"Date picker: {date0}")
            ui.text(f"Date picker year: {date0.year if date0 else 'None'}")
            ui.text(f"Date picker month: {date0.month if date0 else 'None'}")
            ui.text(f"Date picker day: {date0.day if date0 else 'None'}")
        with ui.container():
            dates = ui.date_picker(
                label="Dates picker", value=[date.today(), date.today() + timedelta(days=1)], type="multiple"
            )
            ui.text(f"Dates picker: {dates}")
        with ui.container():
            date_range = ui.date_picker(
                label="Date range picker", value=(date.today(), date.today() + timedelta(days=1)), type="range"
            )
            ui.text(f"Date range picker: {date_range}")

    ui.header("Date picker input")
    with ui.group():
        with ui.container():
            date_picker_input = ui.date_picker_input(label="Date picker input", value=date.today())
            ui.text(f"Date picker input: {date_picker_input}")
        with ui.container():
            date_picker_input2 = ui.date_picker_input(
                label="Date picker input 2", value=date.today(), left_section=ui.icon("Calendar"), dropdown_type="modal"
            )
            ui.text(f"Date picker input 2: {date_picker_input2}")
        with ui.container():
            dates2 = ui.date_picker_input(
                label="Dates picker input", value=[date.today(), date.today() + timedelta(days=1)], type="multiple"
            )
            ui.text(f"Dates picker input: {dates2}")
        with ui.container():
            date_range2 = ui.date_picker_input(
                label="Date range picker input", value=(date.today(), date.today() + timedelta(days=1)), type="range"
            )
            ui.text(f"Date range picker input: {date_range2}")

    ui.header("Time input")
    with ui.group():
        with ui.container():
            time_input = ui.time_input(label="Time input", value=time(12, 30))
            ui.text(f"Time input: {time_input}")
        with ui.container():
            time_input2 = ui.time_input(label="Time input 2", value="12:30", left_section=ui.icon("Clock"))
            ui.text(f"Time input 2: {time_input2}")

    ui.header("Time picker")
    with ui.group():
        with ui.container():
            time_picker = ui.time_picker(label="Time picker", value=time(11, 31), with_seconds=True, with_dropdown=True)
            ui.text(f"Time picker: {time_picker}")
        with ui.container():
            time_picker2 = ui.time_picker(label="Time picker 2", value="10:25", left_section=ui.icon("Clock"))
            ui.text(f"Time picker 2: {time_picker2}")


fruits_data = [
    {
        "date": "Mar 22",
        "Apples": 2890,
        "Oranges": 2338,
        "Tomatoes": 2452,
    },
    {
        "date": "Mar 23",
        "Apples": 2756,
        "Oranges": 2103,
        "Tomatoes": 2402,
    },
    {
        "date": "Mar 24",
        "Apples": 3322,
        "Oranges": 986,
        "Tomatoes": 1821,
    },
    {
        "date": "Mar 25",
        "Apples": 3470,
        "Oranges": 2108,
        "Tomatoes": 2809,
    },
    {
        "date": "Mar 26",
        "Apples": 3129,
        "Oranges": 1726,
        "Tomatoes": 2290,
    },
]


def area_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Area Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Area Chart")
    ui.area_chart(
        data=fruits_data,
        data_key="date",
        series=[
            {"name": "Apples", "color": "indigo.6"},
            {"name": "Oranges", "color": "blue.6"},
            {"name": "Tomatoes", "color": "teal.6"},
        ],
        with_point_labels=True,
        h=300,
        curve_type="linear",
    )
    ui.header("Stacked area chart")
    ui.area_chart(
        data=fruits_data,
        data_key="date",
        series=[
            {"name": "Apples", "color": "indigo.6"},
            {"name": "Oranges", "color": "blue.6"},
            {"name": "Tomatoes", "color": "teal.6"},
        ],
        with_legend=True,
        h=300,
        type="stacked",
    )
    ui.header("Percent area chart")
    ui.area_chart(
        data=fruits_data,
        data_key="date",
        series=[
            {"name": "Apples", "color": "indigo.6"},
            {"name": "Oranges", "color": "blue.6"},
            {"name": "Tomatoes", "color": "teal.6"},
        ],
        type="percent",
        h=300,
    )
    ui.header("Split area chart")
    split_data = [
        {
            "date": "Mar 22",
            "Apples": 110,
        },
        {
            "date": "Mar 23",
            "Apples": 60,
        },
        {
            "date": "Mar 24",
            "Apples": -80,
        },
        {
            "date": "Mar 25",
            "Apples": 40,
        },
        {
            "date": "Mar 26",
            "Apples": -40,
        },
        {
            "date": "Mar 27",
            "Apples": 80,
        },
    ]
    ui.area_chart(
        data=split_data,
        data_key="date",
        series=[{"name": "Apples", "color": "bright"}],
        type="split",
        stroke_width=1,
        dot_props={"r": 2, "strokeWidth": 1},
        active_dot_props={"r": 3, "strokeWidth": 1},
        h=300,
    )


def bar_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Bar Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Bar Chart")
    data = [
        {"month": "January", "Smartphones": 1200, "Laptops": 900, "Tablets": 200},
        {"month": "February", "Smartphones": 1900, "Laptops": 1200, "Tablets": 400},
        {"month": "March", "Smartphones": 400, "Laptops": 1000, "Tablets": 200},
        {"month": "April", "Smartphones": 1000, "Laptops": 200, "Tablets": 800},
        {"month": "May", "Smartphones": 800, "Laptops": 1400, "Tablets": 1200},
        {"month": "June", "Smartphones": 750, "Laptops": 600, "Tablets": 1000},
    ]
    ui.bar_chart(
        data=data,
        data_key="month",
        series=[
            {"name": "Smartphones", "color": "indigo.6"},
            {"name": "Laptops", "color": "blue.6"},
            {"name": "Tablets", "color": "teal.6"},
        ],
        tick_line="y",
        h=300,
    )
    ui.header("Stacked bar chart")
    ui.bar_chart(
        data=data,
        data_key="month",
        with_legend=True,
        series=[
            {"name": "Smartphones", "color": "indigo.6"},
            {"name": "Laptops", "color": "blue.6"},
            {"name": "Tablets", "color": "teal.6"},
        ],
        type="stacked",
        h=300,
    )
    ui.header("Mixed stacked bar chart")
    ui.bar_chart(
        data=data,
        data_key="month",
        series=[
            {"name": "Smartphones", "color": "violet.6", "stackId": "a"},
            {"name": "Laptops", "color": "blue.6", "stackId": "b"},
            {"name": "Tablets", "color": "teal.6", "stackId": "b"},
        ],
        h=300,
    )


def line_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Line Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Line Chart")
    ui.line_chart(
        data=fruits_data,
        data_key="date",
        series=[
            {"name": "Apples", "color": "indigo.6"},
            {"name": "Oranges", "color": "blue.6"},
            {"name": "Tomatoes", "color": "teal.6"},
        ],
        h=300,
        curve_type="linear",
        with_legend=True,
    )
    ui.header("Gradient type")
    data = [
        {"date": "Jan", "temperature": -25},
        {"date": "Feb", "temperature": -10},
        {"date": "Mar", "temperature": 5},
        {"date": "Apr", "temperature": 15},
        {"date": "May", "temperature": 30},
        {"date": "Jun", "temperature": 15},
        {"date": "Jul", "temperature": 30},
        {"date": "Aug", "temperature": 40},
        {"date": "Sep", "temperature": 15},
        {"date": "Oct", "temperature": 20},
        {"date": "Nov", "temperature": 0},
        {"date": "Dec", "temperature": -10},
    ]
    ui.line_chart(
        data=data,
        data_key="date",
        series=[{"name": "temperature", "label": "Avg. Temperature"}],
        h=300,
        type="gradient",
        gradient_stops=[
            {"offset": 0, "color": "red.6"},
            {"offset": 20, "color": "orange.6"},
            {"offset": 40, "color": "yellow.5"},
            {"offset": 70, "color": "lime.5"},
            {"offset": 80, "color": "cyan.5"},
            {"offset": 100, "color": "blue.5"},
        ],
        stroke_width=5,
        curve_type="natural",
        y_axis_props={"domain": [-25, 40]},
    )
    ui.header("Right Y axis")
    biaxialData = [
        {"name": "Page A", "uv": 4000, "pv": 2400},
        {"name": "Page B", "uv": 3000, "pv": 1398},
        {"name": "Page C", "uv": 2000, "pv": 9800},
        {"name": "Page D", "uv": 2780, "pv": 3908},
        {"name": "Page E", "uv": 1890, "pv": 4800},
        {"name": "Page F", "uv": 2390, "pv": 3800},
        {"name": "Page G", "uv": 3490, "pv": 4300},
    ]
    ui.line_chart(
        data=biaxialData,
        data_key="name",
        series=[
            {"name": "uv", "color": "indigo.6"},
            {"name": "pv", "color": "blue.6", "yAxisId": "right"},
        ],
        h=300,
        with_right_y_axis=True,
        y_axis_label="uv",
        right_y_axis_label="pv",
    )


def composite_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Composite Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Composite Chart")
    ui.composite_chart(
        data=fruits_data,
        data_key="date",
        series=[
            {"name": "Tomatoes", "color": "rgba(18, 120, 255, 0.2)", "type": "bar"},
            {"name": "Apples", "color": "red.8", "type": "line"},
            {"name": "Oranges", "color": "yellow.8", "type": "area"},
        ],
        max_bar_width=30,
        h=300,
        curve_type="linear",
    )


countries_data = [
    {"name": "USA", "value": 400, "color": "indigo.6"},
    {"name": "India", "value": 300, "color": "yellow.6"},
    {"name": "Japan", "value": 100, "color": "teal.6"},
    {"name": "Other", "value": 200, "color": "gray.6"},
]


def donut_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Donut Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Donut Chart")
    ui.donut_chart(
        data=countries_data,
        with_labels_line=True,
        labels_type="value",
        with_labels=True,
    )


def pie_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Pie Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Pie Chart")
    ui.pie_chart(
        data=countries_data,
        with_labels_line=True,
        labels_type="value",
        labels_position="outside",
        with_labels=True,
        mx="auto",
    )
    ui.header("Segments labels")
    ui.pie_chart(
        data=countries_data,
        with_labels_line=True,
        labels_type="value",
        labels_position="outside",
        with_labels=True,
        with_tooltip=True,
        tooltip_data_source="segment",
        mx="auto",
    )


def radar_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Radar Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Radar Chart")
    sales = [
        {
            "product": "Apples",
            "Sales January": 120,
            "Sales February": 100,
        },
        {
            "product": "Oranges",
            "Sales January": 98,
            "Sales February": 90,
        },
        {
            "product": "Tomatoes",
            "Sales January": 86,
            "Sales February": 70,
        },
        {
            "product": "Grapes",
            "Sales January": 99,
            "Sales February": 80,
        },
        {
            "product": "Bananas",
            "Sales January": 85,
            "Sales February": 120,
        },
        {
            "product": "Lemons",
            "Sales January": 65,
            "Sales February": 150,
        },
    ]
    ui.radar_chart(
        data=sales,
        data_key="product",
        series=[{"name": "Sales January", "color": "indigo.6", "opacity": 0.5}],
        h=300,
        with_polar_angle_axis=True,
    )
    ui.header("Multiple series")
    ui.radar_chart(
        data=sales,
        data_key="product",
        series=[
            {"name": "Sales January", "color": "indigo.6", "opacity": 0.5},
            {"name": "Sales February", "color": "blue.6", "opacity": 0.5},
        ],
        h=300,
    )


def scatter_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Scatter Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Scatter Chart")
    import random

    group_data = [
        {
            "color": "blue.5",
            "name": "Group 1",
            "data": [{"age": random.randint(18, 65), "BMI": random.randint(10, 40)} for _ in range(10)],  # noqa: S311
        }
    ]
    ui.scatter_chart(
        data=group_data,
        data_key={"x": "age", "y": "BMI"},
        x_axis_label="Age",
        y_axis_label="BMI",
        h=300,
    )
    ui.header("Multiple groups")
    group_data = [
        {
            "color": "blue.5",
            "name": "Group 1",
            "data": [{"age": random.randint(18, 65), "BMI": random.randint(10, 40)} for _ in range(10)],  # noqa: S311
        },
        {
            "color": "red.5",
            "name": "Group 2",
            "data": [{"age": random.randint(18, 65), "BMI": random.randint(10, 40)} for _ in range(10)],  # noqa: S311
        },
    ]
    ui.scatter_chart(
        data=group_data,
        data_key={"x": "age", "y": "BMI"},
        x_axis_label="Age",
        y_axis_label="BMI",
        h=300,
        with_legend=True,
    )


def funnel_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Funnel Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Funnel Chart")
    ui.funnel_chart(
        data=countries_data,
        with_labels=True,
        with_tooltip=True,
        tooltip_data_source="segment",
        mx="auto",
    )


def bubble_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Bubble Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Bubble Chart")
    data = [
        {"hour": "08:00", "index": 1, "value": 150},
        {"hour": "10:00", "index": 2, "value": 166},
        {"hour": "12:00", "index": 3, "value": 170},
        {"hour": "14:00", "index": 4, "value": 150},
        {"hour": "16:00", "index": 2, "value": 200},
        {"hour": "18:00", "index": 4, "value": 400},
        {"hour": "20:00", "index": 3, "value": 100},
        {"hour": "22:00", "index": 1, "value": 160},
    ]
    ui.bubble_chart(
        data=data,
        range=(16, 225),
        label="Sales/hour",
        color="lime.6",
        data_key={"x": "hour", "y": "index", "z": "value"},
        h=300,
    )


def radial_bar_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Radial Bar Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Radial Bar Chart")
    data = [
        {"name": "18-24", "value": 31.47, "color": "blue.7"},
        {"name": "25-29", "value": 26.69, "color": "orange.6"},
        {"name": "30-34", "value": 15.69, "color": "yellow.7"},
        {"name": "35-39", "value": 8.22, "color": "cyan.6"},
        {"name": "40-49", "value": 8.63, "color": "green"},
        {"name": "50+", "value": 2.63, "color": "pink"},
        {"name": "unknown", "value": 6.67, "color": "gray"},
    ]
    ui.radial_bar_chart(
        data=data,
        data_key="name",
        h=220,
        with_legend=True,
    )


def sparkline_chart_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Sparkline Chart")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Sparkline Chart")
    data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    ui.sparkline_chart(
        data=data,
        h=60,
        curve_type="linear",
        color="indigo.6",
        fill_opacity=0.6,
        stroke_width=2,
    )

    positiveTrend = [10, 20, 40, 20, 40, 10, 50]
    negativeTrend = [50, 40, 20, 40, 20, 40, 10]
    neutralTrend = [10, 20, 40, 20, 40, 10, 50, 5, 10]
    ui.header("Positive trend")
    ui.sparkline_chart(
        data=positiveTrend,
        h=60,
        trend_colors={"positive": "teal.6", "negative": "red.6", "neutral": "gray.6"},
    )
    ui.header("Negative trend")
    ui.sparkline_chart(
        data=negativeTrend,
        h=60,
        trend_colors={"positive": "teal.6", "negative": "red.6", "neutral": "gray.6"},
    )
    ui.header("Neutral trend")
    ui.sparkline_chart(
        data=neutralTrend,
        h=60,
        trend_colors={"positive": "teal.6", "negative": "red.6", "neutral": "gray.6"},
    )


def heatmap_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Heatmap")
    with ui.sidebar:
        sidebar_view(ui)
    ui.title("Heatmap")
    import random
    from datetime import datetime, timedelta

    start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    data = {}
    for i in range(365):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        data[date_str] = random.randint(0, 10)  # noqa: S311
    min_date = min(data.keys())
    max_date = max(data.keys())
    get_tooltip_label = """
    const { date, value } = arguments[0];
    return `${date} | ${value || 0}`;
    """
    with ui.scroll_area():
        ui.heatmap(
            data=data,
            start_date=min_date,
            end_date=max_date,
            first_day_of_week=0,
            with_tooltip=True,
            with_outside_dates=True,
            with_weekday_labels=True,
            with_month_labels=True,
            get_tooltip_label=get_tooltip_label,
        )
    ui.header("Change colors")

    with ui.scroll_area():
        colors = [
            "yellow",
            "var(--mantine-color-orange-4)",
            "var(--mantine-color-orange-6)",
            "var(--mantine-color-orange-7)",
            "var(--mantine-color-orange-9)",
            "brown",
        ]
        ui.heatmap(
            data=data,
            start_date=min_date,
            end_date=max_date,
            first_day_of_week=0,
            with_tooltip=True,
            with_outside_dates=True,
            with_weekday_labels=True,
            with_month_labels=True,
            get_tooltip_label=get_tooltip_label,
            colors=colors,
        )


@app.route("/layouts", methods=["GET", "POST"])
def layouts() -> Response:
    return routelit_adapter.stream_response(layouts_view)


@app.route("/checkboxes", methods=["GET", "POST"])
def checkboxes() -> Response:
    return routelit_adapter.stream_response(checkboxes_view)


@app.route("/chips", methods=["GET", "POST"])
def chips() -> Response:
    return routelit_adapter.stream_response(chips_view)


@app.route("/inputs", methods=["GET", "POST"])
def inputs() -> Response:
    return routelit_adapter.stream_response(inputs_view)


@app.route("/combobox", methods=["GET", "POST"])
def combobox() -> Response:
    return routelit_adapter.stream_response(combobox_view)


@app.route("/buttons", methods=["GET", "POST"])
def buttons() -> Response:
    return routelit_adapter.stream_response(buttons_view)


@app.route("/feedback", methods=["GET", "POST"])
def feedback() -> Response:
    return routelit_adapter.stream_response(feedback_view)


@app.route("/overlays", methods=["GET", "POST"])
def overlays() -> Response:
    return routelit_adapter.stream_response(overlays_view)


@app.route("/navigation", methods=["GET", "POST"])
def navigation() -> Response:
    return routelit_adapter.stream_response(navigation_view)


@app.route("/data_display", methods=["GET", "POST"])
def data_display() -> Response:
    return routelit_adapter.stream_response(data_display_view)


@app.route("/miscellaneous", methods=["GET", "POST"])
def miscellaneous() -> Response:
    return routelit_adapter.stream_response(miscellaneous_view)


@app.route("/dates", methods=["GET", "POST"])
def dates() -> Response:
    return routelit_adapter.stream_response(dates_view)


@app.route("/area_chart", methods=["GET", "POST"])
def area_chart() -> Response:
    return routelit_adapter.stream_response(area_chart_view)


@app.route("/bar_chart", methods=["GET", "POST"])
def bar_chart() -> Response:
    return routelit_adapter.stream_response(bar_chart_view)


@app.route("/line_chart", methods=["GET", "POST"])
def line_chart() -> Response:
    return routelit_adapter.stream_response(line_chart_view)


@app.route("/composite_chart", methods=["GET", "POST"])
def composite_chart() -> Response:
    return routelit_adapter.stream_response(composite_chart_view)


@app.route("/donut_chart", methods=["GET", "POST"])
def donut_chart() -> Response:
    return routelit_adapter.stream_response(donut_chart_view)


@app.route("/pie_chart", methods=["GET", "POST"])
def pie_chart() -> Response:
    return routelit_adapter.stream_response(pie_chart_view)


@app.route("/radar_chart", methods=["GET", "POST"])
def radar_chart() -> Response:
    return routelit_adapter.stream_response(radar_chart_view)


@app.route("/scatter_chart", methods=["GET", "POST"])
def scatter_chart() -> Response:
    return routelit_adapter.stream_response(scatter_chart_view)


@app.route("/funnel_chart", methods=["GET", "POST"])
def funnel_chart() -> Response:
    return routelit_adapter.stream_response(funnel_chart_view)


@app.route("/bubble_chart", methods=["GET", "POST"])
def bubble_chart() -> Response:
    return routelit_adapter.stream_response(bubble_chart_view)


@app.route("/radial_bar_chart", methods=["GET", "POST"])
def radial_bar_chart() -> Response:
    return routelit_adapter.stream_response(radial_bar_chart_view)


@app.route("/sparkline_chart", methods=["GET", "POST"])
def sparkline_chart() -> Response:
    return routelit_adapter.stream_response(sparkline_chart_view)


@app.route("/heatmap", methods=["GET", "POST"])
def heatmap() -> Response:
    return routelit_adapter.stream_response(heatmap_view)


@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    return routelit_adapter.stream_response(index_view)


@app.route("/hello", methods=["GET", "POST"])
def hello() -> Response:
    return {"name": "John Doe"}


if __name__ == "__main__":
    app.run(debug=True)  # noqa: S201
