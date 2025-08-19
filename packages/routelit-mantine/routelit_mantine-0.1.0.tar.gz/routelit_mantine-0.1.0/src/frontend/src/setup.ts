import {
  componentStore,
  withSimpleComponent,
  withEventDispatcher,
  withValueEventDispatcher,
  withInputValueEventDispatcher,
  withCallbackAttributes,
} from "routelit-client";
import {
  Space,
  Stack,
  SimpleGrid,
  Group,
  Grid,
  Container,
  Flex,
  AppShell,
  Checkbox,
  Chip,
  ColorInput,
  Fieldset,
  TextInput,
  NativeSelect,
  Select,
  NumberInput,
  PasswordInput,
  RangeSlider,
  Rating,
  SegmentedControl,
  Slider,
  Switch,
  Textarea,
  Autocomplete,
  MultiSelect,
  TagsInput,
  ActionIcon as MantineActionIcon,
  Button,
  Tabs,
  Alert,
  Notification,
  Progress,
  Dialog,
  Drawer,
  Modal,
  Affix,
  Image,
  NumberFormatter,
  Spoiler,
  Text,
  Title,
  Table,
  Box,
  Paper,
  ScrollArea,
  Accordion,
} from "@mantine/core";
import {
  DatePicker,
  TimeInput,
  TimePicker,
  DateTimePicker,
  DatePickerInput,
} from "@mantine/dates";
import {
  AreaChart,
  BarChart,
  LineChart,
  CompositeChart,
  DonutChart,
  FunnelChart,
  PieChart,
  RadarChart,
  ScatterChart,
  BubbleChart,
  RadialBarChart,
  Sparkline,
  Heatmap
} from "@mantine/charts";
import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/charts/styles.css";
import "./lib.css";
import { RLAppShell, RLProvider } from "./components";
import ChipGroup from "./components/chip-group";
import RadioGroup from "./components/radio-group";
import CheckboxGroup from "./components/checkbox-group";
import SwitchGroup from "./components/switch-group";
import { ActionIcon } from "./components/action-icon";
import TablerIcon from "./components/icon";
import Anchor from "./components/anchor";
import NavLink from "./components/nav-link";

const idFn = (value: unknown) => value;

componentStore.register("provider", RLProvider);
componentStore.register("appshell", RLAppShell);
componentStore.register(
  "navbar",
  withSimpleComponent(AppShell.Navbar, { p: "sm" })
);
componentStore.register("main", AppShell.Main);
componentStore.register("container", Container);
componentStore.register("flex", Flex);
componentStore.register("grid", Grid);
componentStore.register("gridcol", Grid.Col);
componentStore.register("group", Group);
componentStore.register("simplegrid", SimpleGrid);
componentStore.register("space", Space);
componentStore.register("stack", Stack);
componentStore.register(
  "checkbox",
  withValueEventDispatcher(Checkbox, {
    rlValueAttr: "checked",
    rlEventValueGetter: (e: React.ChangeEvent<HTMLInputElement>) =>
      e.currentTarget.checked,
  })
);
componentStore.register(
  "checkboxgroup",
  withValueEventDispatcher(CheckboxGroup, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "chip",
  withValueEventDispatcher(Chip, {
    rlValueAttr: "checked",
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: ["icon"],
  })
);
componentStore.register(
  "chipgroup",
  withValueEventDispatcher(ChipGroup, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "colorinput",
  withValueEventDispatcher(ColorInput, {
    rlEventAttr: "onChangeEnd",
    rlEventValueGetter: idFn,
  })
);
componentStore.register("fieldset", Fieldset);
componentStore.register(
  "textinput",
  withInputValueEventDispatcher(TextInput, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "nativeselect",
  withValueEventDispatcher(NativeSelect, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "numberinput",
  withInputValueEventDispatcher(NumberInput, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "passwordinput",
  withInputValueEventDispatcher(PasswordInput)
);
componentStore.register(
  "radiogroup",
  withValueEventDispatcher(RadioGroup, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "rangeslider",
  withValueEventDispatcher(RangeSlider, {
    rlEventAttr: "onChangeEnd",
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "rating",
  withValueEventDispatcher(Rating, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "segmentedcontrol",
  withValueEventDispatcher(SegmentedControl, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "slider",
  withValueEventDispatcher(Slider, {
    rlEventAttr: "onChangeEnd",
    rlEventValueGetter: idFn,
  })
);
componentStore.register(
  "switch",
  withValueEventDispatcher(Switch, {
    rlValueAttr: "checked",
    rlEventValueGetter: (e: React.ChangeEvent<HTMLInputElement>) =>
      e.currentTarget.checked,
    rlInlineElementsAttrs: ["thumbIcon"],
  })
);
componentStore.register(
  "switchgroup",
  withValueEventDispatcher(SwitchGroup, {
    rlEventValueGetter: idFn,
  })
);
componentStore.register("textarea", withInputValueEventDispatcher(Textarea));
componentStore.register(
  "autocomplete",
  withInputValueEventDispatcher(Autocomplete, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "multiselect",
  withValueEventDispatcher(MultiSelect, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "select",
  withValueEventDispatcher(Select, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register(
  "tagsinput",
  withValueEventDispatcher(TagsInput, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register("actionicon", withEventDispatcher(ActionIcon));
componentStore.register("actionicongroup", MantineActionIcon.Group);
componentStore.register(
  "actionicongroupsection",
  MantineActionIcon.GroupSection
);
componentStore.register("icon", TablerIcon);
componentStore.register(
  "button",
  withEventDispatcher(Button, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register("anchor", Anchor);
componentStore.register("link", Anchor);
componentStore.register(
  "navlink",
  withSimpleComponent(NavLink, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register("tabs", Tabs);
componentStore.register(
  "tab",
  withSimpleComponent(Tabs.Tab, {
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register("tablist", Tabs.List);
componentStore.register("tabpanel", Tabs.Panel);
componentStore.register(
  "alert",
  withEventDispatcher(Alert, {
    rlEventName: "close",
    rlEventAttr: "onClose",
    rlInlineElementsAttrs: ["icon"],
  })
);
componentStore.register(
  "notification",
  withEventDispatcher(Notification, {
    rlEventName: "close",
    rlEventAttr: "onClose",
    rlInlineElementsAttrs: ["icon"],
  })
);
componentStore.register("progress", Progress);
componentStore.register(
  "dialog",
  withEventDispatcher(Dialog, {
    rlEventName: "close",
    rlEventAttr: "onClose",
  })
);
componentStore.register(
  "drawer",
  withEventDispatcher(Drawer, {
    rlEventName: "close",
    rlEventAttr: "onClose",
  })
);
componentStore.register(
  "modal",
  withEventDispatcher(Modal, {
    rlEventName: "close",
    rlEventAttr: "onClose",
  })
);
componentStore.register("affix", Affix);
componentStore.register("image", Image);
componentStore.register("numberformatter", NumberFormatter);
componentStore.register("spoiler", Spoiler);
componentStore.register("text", Text);
componentStore.register("title", Title);
componentStore.register("table", Table);
componentStore.register("tablehead", Table.Thead);
componentStore.register("tablebody", Table.Tbody);
componentStore.register("tablefoot", Table.Tfoot);
componentStore.register("tablerow", Table.Tr);
componentStore.register("tablecell", Table.Td);
componentStore.register("tableheader", Table.Th);
componentStore.register("tablecaption", Table.Caption);
componentStore.register("tablescrollcontainer", Table.ScrollContainer);
componentStore.register("box", Box);
componentStore.register("paper", Paper);
componentStore.register("scrollarea", ScrollArea);
componentStore.register(
  "datepicker",
  withValueEventDispatcher(DatePicker, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: ["leftSection", "rightSection"],
  })
);
componentStore.register("timeinput",  withValueEventDispatcher(TimeInput, {
  rlInlineElementsAttrs: [
    "leftSection",
    "rightSection",
  ],
}));
componentStore.register("timepicker", withValueEventDispatcher(TimePicker, {
  rlEventValueGetter: idFn,
  rlInlineElementsAttrs: [
    "leftSection",
    "rightSection",
  ],
}));
componentStore.register(
  "datetimepicker",
  withValueEventDispatcher(DateTimePicker, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: [
      "leftSection",
      "rightSection",
      "nextIcon",
      "previousIcon",
    ],
  })
);
componentStore.register(
  "datepickerinput",
  withValueEventDispatcher(DatePickerInput, {
    rlEventValueGetter: idFn,
    rlInlineElementsAttrs: [
      "leftSection",
      "rightSection",
      "nextIcon",
      "previousIcon",
    ],
  })
);
componentStore.register("accordion", withSimpleComponent(Accordion, {
  rlInlineElementsAttrs: ["chevron"],
}));
componentStore.register("accordionitem", Accordion.Item);
componentStore.register("accordionpanel", Accordion.Panel);
componentStore.register("accordioncontrol", withSimpleComponent(Accordion.Control, {
  rlInlineElementsAttrs: ["chevron", "icon"],
}));
componentStore.register("areachart", AreaChart);
componentStore.register("barchart", BarChart);
componentStore.register("linechart", LineChart);
componentStore.register("compositechart", CompositeChart);
componentStore.register("donutchart", DonutChart);
componentStore.register("funnelchart", FunnelChart);
componentStore.register("piechart", PieChart);
componentStore.register("radarchart", RadarChart);
componentStore.register("scatterchart", ScatterChart);
componentStore.register("bubblechart", BubbleChart);
componentStore.register("radialbarchart", RadialBarChart);
componentStore.register("sparkline", Sparkline);
componentStore.register("heatmap", withCallbackAttributes(Heatmap, {
  rlCallbackAttrs: ["getTooltipLabel"],
  getTooltipLabel: ({ date, value }) => `${date} | ${value}`,
}));
componentStore.forceUpdate();
