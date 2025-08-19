import datetime
from typing import Any, Callable, ClassVar, Literal, Optional, TypedDict, Union, cast

from routelit import AssetTarget, RLOption, RouteLitBuilder, RouteLitElement


class GroupOption(TypedDict):
    """
    A group option for a checkbox group.
    """

    group: str
    items: list[str]


class MTTab(TypedDict, total=False):
    """
    A tab for a tablist.
    """

    value: str
    label: Optional[str]
    color: Optional[str]
    left_section: Optional[RouteLitElement]
    right_section: Optional[RouteLitElement]
    size: Optional[Union[str, int]]
    keep_mounted: Optional[bool]
    children: Optional[str]  # For internal use
    leftSection: Optional[RouteLitElement]  # For internal use
    rightSection: Optional[RouteLitElement]  # For internal use


class RLBuilder(RouteLitBuilder):
    """
    A builder for a RouteLit application.
    This Builder template serves as example on how to create a RouteLit custom components.
    """

    static_assets_targets: ClassVar[list[AssetTarget]] = [
        {
            "package_name": "routelit_mantine",
            "path": "static",
        }
    ]

    def _init_root(self) -> "RLBuilder":
        new_element = self._create_element(
            name="provider",
            key="provider",
            props={
                "defaultColorScheme": "auto",
                "theme": {
                    "primaryColor": "orange",
                },
            },
            virtual=True,
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def _init_app_shell(self) -> "RLBuilder":
        new_element = self._create_element(
            name="appshell",
            key="__appshell__",
            props={},
            virtual=True,
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def _init_navbar(self) -> "RLBuilder":
        new_element = self._create_element(
            name="navbar",
            key="__navbar__",
            props={},
            virtual=True,
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def _init_main(self) -> "RLBuilder":
        new_element = self._create_element(
            name="main",
            key="__main__",
            props={},
            virtual=True,
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def _on_init(self) -> None:
        self._root = self._init_root()
        with self._root:
            self._app_shell = self._init_app_shell()
            with self._app_shell:
                self._navbar = self._init_navbar()
                self._main = self._init_main()
        self._parent_element = self._main._parent_element
        self.active_child_builder = self._main

    def set_provider_props(self, theme: dict[str, Any], **kwargs: Any) -> None:
        """
        Set the provider props.

        Args:
            theme (dict[str, Any]): The theme to set.
            kwargs: Additional props to set.
        """
        self._root.root_element.props.update(kwargs)
        self._root.root_element.props["theme"] = theme

    def set_app_shell_props(
        self,
        title: Optional[str] = None,
        logo: Optional[str] = None,
        navbar_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Set the app shell props.

        Args:
            title (Optional[str]): The title of the app shell.
            logo (Optional[str]): The logo of the app shell.
            navbar_props (Optional[dict[str, Any]]): The props of the navbar.
            kwargs: Additional props to set.
        """
        self._app_shell.root_element.props.update(kwargs)
        self._app_shell.root_element.props["title"] = title
        self._app_shell.root_element.props["logo"] = logo
        self._app_shell.root_element.props["navbarProps"] = navbar_props

    @property
    def sidebar(self) -> "RLBuilder":
        """
        Get the sidebar builder.

        Returns:
            RLBuilder: The sidebar builder.

        Example:
        ```python
        with ui.sidebar:
            ui.subheader("Sidebar")

        # or

        ui.sidebar.subheader("Sidebar")
        ```
        """
        return self._navbar

    def container(  # type: ignore[override]
        self,
        *,
        fluid: bool = False,
        key: Optional[str] = None,
        size: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a container.

        Args:
            fluid (bool): Whether the container is fluid.
            key (Optional[str]): The key of the container.
            size (Optional[str]): The size of the container.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: The container builder.

        Example:
        ```python
        with ui.container(fluid=True, size="xl", bg="var(--mantine-color-blue-light)"):
            ui.text("Hello World")
        """
        new_element = self._create_element(
            key=key or self._new_text_id("container"),
            name="container",
            props={"fluid": fluid, "size": size, **kwargs},
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def flex(  # type: ignore[override]
        self,
        *,
        align: Optional[str] = None,
        column_gap: Optional[str] = None,
        direction: Optional[str] = None,
        gap: Optional[str] = None,
        justify: Optional[str] = None,
        key: Optional[str] = None,
        row_gap: Optional[str] = None,
        wrap: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a flex.

        Args:
            align (Optional[str]): The alignment of the flex.
            column_gap (Optional[str]): The gap between columns.
            direction (Optional[str]): The direction of the flex.
            gap (Optional[str]): The gap between items.
            justify (Optional[str]): The justification of the flex.
            key (Optional[str]): The key of the flex.
            row_gap (Optional[str]): The gap between rows.
            wrap (Optional[str]): The wrapping of the flex.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: The flex builder.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("flex"),
            name="flex",
            props={
                "align": align,
                "columnGap": column_gap,
                "direction": direction,
                "gap": gap,
                "justify": justify,
                "rowGap": row_gap,
                "wrap": wrap,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def grid(
        self,
        *,
        align: Optional[str] = None,
        breakpoints: Optional[dict] = None,
        columns: Optional[int] = None,
        grow: Optional[bool] = None,
        gutter: Optional[dict] = None,
        justify: Optional[str] = None,
        key: Optional[str] = None,
        overflow: Optional[str] = None,
        query_type: Optional[Literal["media", "container"]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a responsive grid container.

        Args:
            align (Optional[str]): Vertical alignment of grid content.
            breakpoints (Optional[dict]): Responsive column settings per breakpoint.
            columns (Optional[int]): Number of columns.
            grow (Optional[bool]): Whether columns should grow to fill available space.
            gutter (Optional[dict]): Spacing configuration between columns/rows.
            justify (Optional[str]): Horizontal justification of grid content.
            key (Optional[str]): Explicit element key.
            overflow (Optional[str]): Overflow behavior.
            query_type (Optional[Literal["media", "container"]]): Type of responsive query to use.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the created grid element.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("grid"),
            name="grid",
            props={
                "align": align,
                "breakpoints": breakpoints,
                "columns": columns,
                "grow": grow,
                "gutter": gutter,
                "justify": justify,
                "overflow": overflow,
                "type": query_type,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def grid_col(
        self,
        *,
        key: Optional[str] = None,
        offset: Optional[int] = None,
        order: Optional[int] = None,
        span: Optional[int] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Add a grid column inside the nearest grid.

        Args:
            key (Optional[str]): Explicit element key.
            offset (Optional[int]): Column offset.
            order (Optional[int]): Column order.
            span (Optional[int]): How many columns the item spans.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the grid column element.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("gridcol"),
            name="gridcol",
            props={
                "offset": offset,
                "order": order,
                "span": span,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def group(
        self,
        *,
        align: Optional[str] = None,
        gap: Optional[str] = None,
        grow: Optional[bool] = None,
        justify: Optional[str] = None,
        key: Optional[str] = None,
        prevent_grow_overflow: Optional[bool] = None,
        wrap: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Arrange children horizontally with spacing and alignment.

        Args:
            align (Optional[str]): Vertical alignment of items.
            gap (Optional[str]): Spacing between items.
            grow (Optional[bool]): Allow items to grow to fill the row.
            justify (Optional[str]): Horizontal alignment of items.
            key (Optional[str]): Explicit element key.
            prevent_grow_overflow (Optional[bool]): Prevent overflow when items grow.
            wrap (Optional[str]): Wrapping behavior.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the group element.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("group"),
            name="group",
            props={
                "align": align,
                "gap": gap,
                "grow": grow,
                "justify": justify,
                "preventGrowOverflow": prevent_grow_overflow,
                "wrap": wrap,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def simple_grid(
        self,
        *,
        cols: Optional[int] = None,
        key: Optional[str] = None,
        query_type: Optional[Literal["media", "container"]] = None,
        spacing: Optional[str] = None,
        vertical_spacing: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a simplified responsive grid.

        Args:
            cols (Optional[int]): Number of columns.
            key (Optional[str]): Explicit element key.
            query_type (Optional[Literal["media", "container"]]): Responsive query type.
            spacing (Optional[str]): Spacing between items.
            vertical_spacing (Optional[str]): Vertical spacing between rows.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the simple grid element.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("simplegrid"),
            name="simplegrid",
            props={
                "cols": cols,
                "spacing": spacing,
                "type": query_type,
                "verticalSpacing": vertical_spacing,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def space(
        self,
        *,
        h: Optional[str] = None,
        key: Optional[str] = None,
        v: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Insert vertical and/or horizontal space.

        Args:
            h (Optional[str]): Horizontal space size (e.g., CSS length).
            key (Optional[str]): Explicit element key.
            v (Optional[str]): Vertical space size (e.g., CSS length).
            kwargs: Additional props to set.
        """
        self._create_element(
            key=key or self._new_text_id("space"),
            name="space",
            props={"h": h, "v": v, **kwargs},
        )

    def stack(
        self,
        *,
        align: Optional[str] = None,
        gap: Optional[str] = None,
        justify: Optional[str] = None,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Stack children vertically with spacing and alignment.

        Args:
            align (Optional[str]): Horizontal alignment of items.
            gap (Optional[str]): Spacing between items.
            justify (Optional[str]): Vertical alignment of items.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the stack element.
        """
        new_element = self._create_element(
            key=key or self._new_text_id("stack"),
            name="stack",
            props={
                "align": align,
                "gap": gap,
                "justify": justify,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(new_element))

    def checkbox(
        self,
        label: str,
        *,
        auto_contrast: Optional[bool] = None,
        checked: bool = False,
        color: Optional[str] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        icon_color: Optional[str] = None,
        key: Optional[str] = None,
        label_position: Optional[Literal["left", "right"]] = None,
        name: Optional[str] = None,
        on_change: Optional[Callable[[bool], None]] = None,
        radius: Optional[Union[Literal["xs", "sm", "md", "lg", "xl"], int]] = None,
        size: Optional[Literal["xs", "sm", "md", "lg", "xl"]] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Boolean input rendered as a single checkbox.

        Args:
            label (str): Checkbox label.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            checked (bool): Initial checked state.
            color (Optional[str]): Accent color.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            icon_color (Optional[str]): Color of the check icon.
            key (Optional[str]): Explicit element key.
            label_position (Optional[Literal["left", "right"]]): Label position.
            name (Optional[str]): Input name.
            on_change (Optional[Callable[[bool], None]]): Change handler.
            radius (Optional[Union[Literal["xs", "sm", "md", "lg", "xl"], int]]): Corner radius.
            size (Optional[Literal["xs", "sm", "md", "lg", "xl"]]): Control size.
            kwargs: Additional props to set.

        Returns:
            bool: Current value.
        """
        return self._x_checkbox(
            "checkbox",
            key or self._new_widget_id("checkbox", label),
            autoContrast=auto_contrast,
            checked=checked,
            color=color,
            description=description,
            disabled=disabled,
            error=error,
            iconColor=icon_color,
            label=label,
            labelPosition=label_position,
            name=name,
            on_change=on_change,
            radius=radius,
            size=size,
            **kwargs,
        )

    def checkbox_group(  # type: ignore[override]
        self,
        label: str,
        options: list[Union[RLOption, str]],
        *,
        description: Optional[str] = None,
        error: Optional[str] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        group_props: Optional[dict[str, Any]] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[list[str]], None]] = None,
        radius: Optional[Union[str, int]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        size: Optional[str] = None,
        value: Optional[list[str]] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Multiple selection using a group of checkboxes.

        Args:
            label (str): Group label.
            options (list[Union[RLOption, str]]): Available options.
            description (Optional[str]): Helper text under the label.
            error (Optional[str]): Error message.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            group_props (Optional[dict[str, Any]]): Extra props for the group container.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[list[str]], None]]): Change handler.
            radius (Optional[Union[str, int]]): Corner radius.
            read_only (Optional[bool]): Read-only state.
            required (Optional[bool]): Mark as required.
            size (Optional[str]): Control size.
            value (Optional[list[str]]): Selected values.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            list[str]: Selected values.
        """
        return self._x_checkbox_group(
            "checkboxgroup",
            key or self._new_widget_id("checkbox-group", label),
            description=description,
            error=error,
            format_func=format_func,
            groupProps=group_props,
            label=label,
            on_change=on_change,
            options=options,  # type: ignore[arg-type]
            radius=radius,
            readOnly=read_only,
            required=required,
            size=size,
            value=value,
            withAsterisk=with_asterisk,
            **kwargs,
        )

    def chip_group(
        self,
        key: str,
        options: list[Union[RLOption, str]],
        *,
        format_func: Optional[Callable[[Any], str]] = None,
        group_props: Optional[dict[str, Any]] = None,
        multiple: bool = False,
        on_change: Optional[Callable[[Union[str, list[str]]], None]] = None,
        value: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> Union[str, list[str]]:
        """
        Single or multiple selection using chip components.

        Args:
            key (str): Explicit element key.
            options (list[Union[RLOption, str]]): Available options.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            group_props (Optional[dict[str, Any]]): Extra props for the group container.
            multiple (bool): Enable multiple selection.
            on_change (Optional[Callable[[Union[str, list[str]]], None]]): Change handler.
            value (Optional[Union[str, list[str]]]): Selected value(s).
            kwargs: Additional props to set.

        Returns:
            Union[str, list[str]]: Selected value(s).
        """
        if multiple:
            return self._x_checkbox_group(
                "chipgroup",
                key,
                format_func=format_func,
                groupProps=group_props,
                multiple=True,
                on_change=on_change,
                options=options,  # type: ignore[arg-type]
                value=value,  # type: ignore[arg-type]
                **kwargs,
            )
        return self._x_radio_select(  # type: ignore[no-any-return]
            "chipgroup",
            key,
            format_func=format_func,
            groupProps=group_props,
            multiple=False,
            on_change=on_change,
            options=options,  # type: ignore[arg-type]
            value=value,
            **kwargs,
        )

    def chip(
        self,
        label: str,
        *,
        auto_contrast: Optional[bool] = None,
        checked: bool = False,
        color: Optional[str] = None,
        disabled: Optional[bool] = None,
        icon: Optional[RouteLitElement] = None,
        input_type: Optional[Literal["checkbox", "radio"]] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[bool], None]] = None,
        radius: Optional[Union[Literal["xs", "sm", "md", "lg", "xl"], int]] = None,
        size: Optional[Literal["xs", "sm", "md", "lg", "xl"]] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Toggleable chip, can behave as checkbox or radio.

        Args:
            label (str): Chip label.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            checked (bool): Initial checked state.
            color (Optional[str]): Accent color.
            disabled (Optional[bool]): Disable interaction.
            icon (Optional[RouteLitElement]): Left section icon.
            input_type (Optional[Literal["checkbox", "radio"]]): Behavior of the chip.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[bool], None]]): Change handler.
            radius (Optional[Union[Literal["xs", "sm", "md", "lg", "xl"], int]]): Corner radius.
            size (Optional[Literal["xs", "sm", "md", "lg", "xl"]]): Control size.
            kwargs: Additional props to set.

        Returns:
            bool: Current value.
        """
        return self._x_checkbox(
            "chip",
            key or self._new_widget_id("chip", label),
            autoContrast=auto_contrast,
            checked=checked,
            children=label,
            color=color,
            disabled=disabled,
            icon=icon,
            on_change=on_change,
            radius=radius,
            size=size,
            type=input_type,
            **kwargs,
        )

    def color_input(
        self,
        label: str,
        *,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        fix_on_blur: Optional[bool] = None,
        input_size: Optional[str] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        radius: Optional[str] = None,
        required: Optional[bool] = None,
        size: Optional[str] = None,
        swatches: Optional[list[str]] = None,
        value: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        with_picker: Optional[bool] = None,
        with_preview: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """
        Text input specialized for color values with a color picker.

        Args:
            label (str): Field label.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            fix_on_blur (Optional[bool]): Normalize value on blur.
            input_size (Optional[str]): Control size.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[str], None]]): Change handler.
            radius (Optional[str]): Corner radius.
            required (Optional[bool]): Mark as required.
            size (Optional[str]): Control size.
            swatches (Optional[list[str]]): Preset color swatches.
            value (Optional[str]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            with_picker (Optional[bool]): Show color picker.
            with_preview (Optional[bool]): Show color preview chip.
            kwargs: Additional props to set.

        Returns:
            str: Current value.
        """
        return self._x_input(  # type: ignore[return-value]
            "colorinput",
            key or self._new_widget_id("colorinput", label),
            description=description,
            disabled=disabled,
            error=error,
            fixOnBlur=fix_on_blur,
            inputSize=input_size,
            label=label,
            on_change=on_change,
            radius=radius,
            required=required,
            size=size,
            swatches=swatches,
            value=value,
            withAsterisk=with_asterisk,
            withPicker=with_picker,
            withPreview=with_preview,
            **kwargs,
        )

    def fieldset(
        self,
        legend: str,
        *,
        disabled: Optional[bool] = None,
        key: Optional[str] = None,
        radius: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Group a set of related form fields under a legend.

        Args:
            legend (str): Legend text.
            disabled (Optional[bool]): Disable all nested inputs.
            key (Optional[str]): Explicit element key.
            radius (Optional[str]): Corner radius.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the fieldset element.
        """
        element = self._create_element(
            key=key or self._new_widget_id("fieldset", legend),
            name="fieldset",
            props={
                "disabled": disabled,
                "legend": legend,
                "radius": radius,
                **kwargs,
            },
        )
        return cast(RLBuilder, self._build_nested_builder(element))

    def text_input(
        self,
        label: str,
        *,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        key: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        value: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """
        Single-line text input.

        Args:
            label (str): Field label.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            key (Optional[str]): Explicit element key.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            on_change (Optional[Callable[[str], None]]): Change handler.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            value (Optional[str]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            str: Current value.
        """
        return cast(
            str,
            self._x_input(
                "textinput",
                key or self._new_widget_id("textinput", label),
                description=description,
                disabled=disabled,
                error=error,
                label=label,
                leftSection=left_section,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                on_change=on_change,
                required=required,
                rightSection=right_section,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                size=size,
                value=value,
                withAsterisk=with_asterisk,
                **kwargs,
            ),
        )

    def native_select(
        self,
        label: str,
        options: list[Union[RLOption, str]],
        *,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        key: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        radius: Optional[str] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        value: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """
        Native HTML select input.

        Args:
            label (str): Field label.
            options (list[Union[RLOption, str]]): Available options.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            key (Optional[str]): Explicit element key.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            on_change (Optional[Callable[[str], None]]): Change handler.
            radius (Optional[str]): Corner radius.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            value (Optional[str]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            str: Current value.
        """
        return cast(
            str,
            self._x_radio_select(
                "nativeselect",
                key or self._new_widget_id("native-select", label),
                description=description,
                disabled=disabled,
                error=error,
                format_func=format_func,
                label=label,
                leftSection=left_section,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                on_change=on_change,
                options=options,  # type: ignore[arg-type]
                options_attr="data",
                radius=radius,
                required=required,
                rightSection=right_section,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                size=size,
                value=value,
                withAsterisk=with_asterisk,
                **kwargs,
            ),
        )

    def number_input(
        self,
        label: str,
        *,
        allow_decimal: Optional[bool] = None,
        allow_leading_zeros: Optional[bool] = None,
        allow_negative: Optional[bool] = None,
        allowed_decimal_separators: Optional[list[str]] = None,
        decimal_scale: Optional[int] = None,
        decimal_separator: Optional[str] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        hide_controls: Optional[bool] = None,
        key: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        max_value: Optional[Union[float, int]] = None,
        min_value: Optional[Union[float, int]] = None,
        on_change: Optional[Callable[[Union[float, int]], None]] = None,
        parser: Callable[[str], Union[float, int]] = float,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        step: Optional[Union[float, int]] = None,
        value: Optional[Union[float, int]] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[float, int]:
        """
        Numeric input with formatting and controls.

        Args:
            label (str): Field label.
            allow_decimal (Optional[bool]): Allow decimal values.
            allow_leading_zeros (Optional[bool]): Permit leading zeros.
            allow_negative (Optional[bool]): Permit negative values.
            allowed_decimal_separators (Optional[list[str]]): Additional decimal separators.
            decimal_scale (Optional[int]): Maximum number of decimal places.
            decimal_separator (Optional[str]): Decimal separator to use.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            hide_controls (Optional[bool]): Hide increment/decrement controls.
            key (Optional[str]): Explicit element key.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            max_value (Optional[Union[float, int]]): Maximum value.
            min_value (Optional[Union[float, int]]): Minimum value.
            on_change (Optional[Callable[[Union[float, int]], None]]): Change handler.
            parser (Callable[[str], Union[float, int]]): Parser for the returned value.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            step (Optional[Union[float, int]]): Step of increment/decrement.
            value (Optional[Union[float, int]]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            Union[float, int]: Current value parsed by the provided parser.
        """
        return parser(
            cast(
                str,
                self._x_input(
                    "numberinput",
                    key or self._new_widget_id("numberinput", label),
                    allowDecimal=allow_decimal,
                    allowLeadingZeros=allow_leading_zeros,
                    allowNegative=allow_negative,
                    allowedDecimalSeparators=allowed_decimal_separators,
                    decimalScale=decimal_scale,
                    decimalSeparator=decimal_separator,
                    description=description,
                    disabled=disabled,
                    error=error,
                    hideControls=hide_controls,
                    label=label,
                    leftSection=left_section,
                    leftSectionProps=left_section_props,
                    leftSectionWidth=left_section_width,
                    max=max_value,
                    min=min_value,
                    on_change=on_change,
                    required=required,
                    rightSection=right_section,
                    rightSectionProps=right_section_props,
                    rightSectionWidth=right_section_width,
                    size=size,
                    step=step,
                    value=value,
                    withAsterisk=with_asterisk,
                    **kwargs,
                ),
            )
        )

    def password_input(
        self,
        label: str,
        *,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        input_size: Optional[str] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        radius: Optional[str] = None,
        required: Optional[bool] = None,
        size: Optional[str] = None,
        value: Optional[str] = None,
        visible: Optional[bool] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Password input with visibility toggle.

        Args:
            label (str): Field label.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable input interaction.
            error (Optional[str]): Error message.
            input_size (Optional[str]): Control size.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[str], None]]): Change handler.
            radius (Optional[str]): Corner radius.
            required (Optional[bool]): Mark as required.
            size (Optional[str]): Control size.
            value (Optional[str]): Current value.
            visible (Optional[bool]): Force visibility of the password.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            Optional[str]: Current value.
        """
        return self._x_input(
            "passwordinput",
            key or self._new_widget_id("passwordinput", label),
            description=description,
            disabled=disabled,
            error=error,
            inputSize=input_size,
            label=label,
            on_change=on_change,
            radius=radius,
            required=required,
            size=size,
            value=value,
            visible=visible,
            withAsterisk=with_asterisk,
            **kwargs,
        )

    def radio_group(
        self,
        label: str,
        options: list[Union[RLOption, str]],
        *,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        group_props: Optional[dict[str, Any]] = None,
        input_size: Optional[str] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        size: Optional[str] = None,
        value: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Single selection using radio inputs.

        Args:
            label (str): Group label.
            options (list[Union[RLOption, str]]): Available options.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            error (Optional[str]): Error message.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            group_props (Optional[dict[str, Any]]): Extra props for the group container.
            input_size (Optional[str]): Control size.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[str], None]]): Change handler.
            read_only (Optional[bool]): Read-only state.
            required (Optional[bool]): Mark as required.
            size (Optional[str]): Control size.
            value (Optional[str]): Selected value.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            Optional[str]: Selected value.
        """
        return cast(
            Optional[str],
            self._x_radio_select(
                "radiogroup",
                key or self._new_widget_id("radio-group", label),
                description=description,
                disabled=disabled,
                error=error,
                format_func=format_func,
                group_props=group_props,
                inputSize=input_size,
                label=label,
                on_change=on_change,
                options=options,  # type: ignore[arg-type]
                readOnly=read_only,
                required=required,
                size=size,
                value=value,
                withAsterisk=with_asterisk,
                **kwargs,
            ),
        )

    def range_slider(
        self,
        label: str,
        *,
        color: Optional[str] = None,
        disabled: Optional[bool] = None,
        inverted: Optional[bool] = None,
        key: Optional[str] = None,
        label_always_on: Optional[bool] = None,
        marks: Optional[list[RLOption]] = None,
        max_range: Optional[float] = None,
        max_value: Optional[float] = None,
        min_value: Optional[float] = None,
        on_change: Optional[Callable[[tuple[float, float]], None]] = None,
        precision: Optional[int] = None,
        step: Optional[float] = None,
        value: Optional[tuple[float, float]] = None,
        **kwargs: Any,
    ) -> tuple[float, float]:
        """
        Slider that allows selecting a numeric range.

        Args:
            label (str): Field label.
            color (Optional[str]): Accent color.
            disabled (Optional[bool]): Disable interaction.
            inverted (Optional[bool]): Invert direction.
            key (Optional[str]): Explicit element key.
            label_always_on (Optional[bool]): Always show labels above thumbs.
            marks (Optional[list[RLOption]]): Marks along the slider.
            max_range (Optional[float]): Max distance between thumbs.
            max_value (Optional[float]): Maximum value.
            min_value (Optional[float]): Minimum value.
            on_change (Optional[Callable[[tuple[float, float]], None]]): Change handler.
            precision (Optional[int]): Decimal precision.
            step (Optional[float]): Step size.
            value (Optional[tuple[float, float]]): Current value.
            kwargs: Additional props to set.

        Returns:
            tuple[float, float]: Current range values.
        """
        return cast(
            tuple[float, float],
            self._x_input(
                "rangeslider",
                key or self._new_widget_id("rangeslider", label),
                color=color,
                disabled=disabled,
                inverted=inverted,
                label=label,
                labelAlwaysOn=label_always_on,
                marks=marks,
                max=max_value,
                maxRange=max_range,
                min=min_value,
                on_change=on_change,
                precision=precision,
                step=step,
                value=value,
                **kwargs,
            ),
        )

    def rating(
        self,
        key: str,
        *,
        color: Optional[str] = None,
        count: Optional[int] = None,
        fractions: Optional[int] = None,
        on_change: Optional[Callable[[int], None]] = None,
        read_only: Optional[bool] = None,
        size: Optional[str] = None,
        parser: Callable[[Any], Union[float, int]] = float,
        value: Optional[int] = None,
        **kwargs: Any,
    ) -> float:
        """
        Star (or icon) rating input.

        Args:
            key (str): Explicit element key.
            color (Optional[str]): Accent color.
            count (Optional[int]): Number of icons.
            fractions (Optional[int]): Fractional steps per icon.
            on_change (Optional[Callable[[int], None]]): Change handler.
            read_only (Optional[bool]): Read-only state.
            size (Optional[str]): Control size.
            parser (Callable[[Any], Union[float, int]]): Parser for the returned value.
            value (Optional[int]): Current value.
            kwargs: Additional props to set.

        Returns:
            float: Current value parsed by the provided parser.
        """
        return parser(
            self._x_input(
                "rating",
                key,
                color=color,
                count=count,
                fractions=fractions,
                on_change=on_change,
                readOnly=read_only,
                size=size,
                value=value,
                **kwargs,
            )
        )

    def segmented_control(
        self,
        key: str,
        options: list[Union[RLOption, str]],
        *,
        auto_contrast: Optional[bool] = None,
        color: Optional[str] = None,
        disabled: Optional[bool] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        full_width: Optional[bool] = None,
        on_change: Optional[Callable[[str], None]] = None,
        orientation: Optional[Literal["horizontal", "vertical"]] = None,
        radius: Optional[str] = None,
        read_only: Optional[bool] = None,
        size: Optional[str] = None,
        transition_duration: Optional[int] = None,
        value: Optional[str] = None,
        with_items_borders: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """
        Segmented control for single selection among options.

        Args:
            key (str): Explicit element key.
            options (list[Union[RLOption, str]]): Available options.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            color (Optional[str]): Accent color.
            disabled (Optional[bool]): Disable interaction.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            full_width (Optional[bool]): Make control take full width.
            on_change (Optional[Callable[[str], None]]): Change handler.
            orientation (Optional[Literal["horizontal", "vertical"]]): Orientation.
            radius (Optional[str]): Corner radius.
            read_only (Optional[bool]): Read-only state.
            size (Optional[str]): Control size.
            transition_duration (Optional[int]): Selection animation duration.
            value (Optional[str]): Selected value.
            with_items_borders (Optional[bool]): Show borders between items.
            kwargs: Additional props to set.

        Returns:
            str: Selected value.
        """
        value = self._x_radio_select(
            "segmentedcontrol",
            key,
            autoContrast=auto_contrast,
            color=color,
            disabled=disabled,
            format_func=format_func,
            fullWidth=full_width,
            on_change=on_change,
            options=options,  # type: ignore[arg-type]
            options_attr="data",
            orientation=orientation,
            radius=radius,
            readOnly=read_only,
            size=size,
            transitionDuration=transition_duration,
            value=value,
            withItemsBorders=with_items_borders,
            **kwargs,
        )
        if value is None and options and len(options) > 0:
            return options[0]["value"] if isinstance(options[0], dict) else options[0]
        return value

    def slider(
        self,
        label: str,
        *,
        disabled: Optional[bool] = None,
        inverted: Optional[bool] = None,
        key: Optional[str] = None,
        label_always_on: Optional[bool] = None,
        marks: Optional[list[RLOption]] = None,
        max_value: Optional[float] = None,
        min_value: Optional[float] = None,
        on_change: Optional[Callable[[float], None]] = None,
        precision: Optional[int] = None,
        restrict_to_marks: Optional[bool] = None,
        show_label_on_hover: Optional[bool] = None,
        size: Optional[str] = None,
        step: Optional[float] = None,
        parser: Callable[[Any], Union[float, int]] = float,
        thumb_label: Optional[str] = None,
        thumb_size: Optional[str] = None,
        value: Optional[float] = None,
        **kwargs: Any,
    ) -> Union[float, int]:
        """
        Single-value slider input.

        Args:
            label (str): Field label.
            disabled (Optional[bool]): Disable interaction.
            inverted (Optional[bool]): Invert direction.
            key (Optional[str]): Explicit element key.
            label_always_on (Optional[bool]): Always show label above thumb.
            marks (Optional[list[RLOption]]): Marks along the slider.
            max_value (Optional[float]): Maximum value.
            min_value (Optional[float]): Minimum value.
            on_change (Optional[Callable[[float], None]]): Change handler.
            precision (Optional[int]): Decimal precision.
            restrict_to_marks (Optional[bool]): Only allow values at marks.
            show_label_on_hover (Optional[bool]): Show label when hovering.
            size (Optional[str]): Control size.
            step (Optional[float]): Step size.
            parser (Callable[[Any], Union[float, int]]): Parser for the returned value.
            thumb_label (Optional[str]): Label template for thumb.
            thumb_size (Optional[str]): Thumb size.
            value (Optional[float]): Current value.
            kwargs: Additional props to set.

        Returns:
            Union[float, int]: Current value parsed by the provided parser.
        """
        return parser(
            self._x_input(
                "slider",
                key or self._new_widget_id("slider", label),
                disabled=disabled,
                inverted=inverted,
                label=label,
                labelAlwaysOn=label_always_on,
                marks=marks,
                max=max_value,
                min=min_value,
                on_change=on_change,
                precision=precision,
                restrictToMarks=restrict_to_marks,
                showLabelOnHover=show_label_on_hover,
                size=size,
                step=step,
                thumbLabel=thumb_label,
                thumbSize=thumb_size,
                value=value,
                **kwargs,
            )
        )

    def switch(
        self,
        label: str,
        *,
        checked: bool = False,
        color: Optional[str] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        key: Optional[str] = None,
        label_position: Optional[Literal["left", "right"]] = None,
        on_change: Optional[Callable[[bool], None]] = None,
        radius: Optional[str] = None,
        size: Optional[str] = None,
        thumb_icon: Optional[RouteLitElement] = None,
        with_thumb_indicator: Optional[bool] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Boolean input rendered as a switch.

        Args:
            label (str): Field label.
            checked (bool): Initial checked state.
            color (Optional[str]): Accent color.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            error (Optional[str]): Error message.
            key (Optional[str]): Explicit element key.
            label_position (Optional[Literal["left", "right"]]): Label position.
            on_change (Optional[Callable[[bool], None]]): Change handler.
            radius (Optional[str]): Corner radius.
            size (Optional[str]): Control size.
            thumb_icon (Optional[RouteLitElement]): Icon inside the thumb.
            with_thumb_indicator (Optional[bool]): Show indicator inside the thumb.
            kwargs: Additional props to set.

        Returns:
            bool: Current value.
        """
        return self._x_checkbox(
            "switch",
            key or self._new_widget_id("switch", label),
            checked=checked,
            color=color,
            description=description,
            disabled=disabled,
            error=error,
            label=label,
            labelPosition=label_position,
            on_change=on_change,
            radius=radius,
            size=size,
            thumbIcon=thumb_icon,
            withThumbIndicator=with_thumb_indicator,
            **kwargs,
        )

    def switch_group(
        self,
        label: str,
        options: list[Union[RLOption, str]],
        *,
        description: Optional[str] = None,
        error: Optional[str] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        group_props: Optional[dict[str, Any]] = None,
        key: Optional[str] = None,
        on_change: Optional[Callable[[list[str]], None]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        size: Optional[str] = None,
        value: Optional[list[str]] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Multiple selection using a group of switches.

        Args:
            label (str): Group label.
            options (list[Union[RLOption, str]]): Available options.
            description (Optional[str]): Helper text under the label.
            error (Optional[str]): Error message.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            group_props (Optional[dict[str, Any]]): Extra props for the group container.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[list[str]], None]]): Change handler.
            read_only (Optional[bool]): Read-only state.
            required (Optional[bool]): Mark as required.
            size (Optional[str]): Control size.
            value (Optional[list[str]]): Selected values.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            list[str]: Selected values.
        """
        return self._x_checkbox_group(
            "switchgroup",
            key or self._new_widget_id("switch-group", label),
            description=description,
            error=error,
            format_func=format_func,
            groupProps=group_props,
            label=label,
            on_change=on_change,
            options=options,  # type: ignore[arg-type]
            readOnly=read_only,
            required=required,
            size=size,
            value=value,
            withAsterisk=with_asterisk,
            **kwargs,
        )

    def textarea(
        self,
        label: str,
        *,
        autosize: Optional[bool] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        error: Optional[str] = None,
        input_size: Optional[str] = None,
        key: Optional[str] = None,
        max_rows: Optional[int] = None,
        min_rows: Optional[int] = None,
        on_change: Optional[Callable[[str], None]] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        resize: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Multi-line text input.

        Args:
            label (str): Field label.
            autosize (Optional[bool]): Grow/shrink to fit content.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            error (Optional[str]): Error message.
            input_size (Optional[str]): Control size.
            key (Optional[str]): Explicit element key.
            max_rows (Optional[int]): Maximum number of rows when autosizing.
            min_rows (Optional[int]): Minimum number of rows when autosizing.
            on_change (Optional[Callable[[str], None]]): Change handler.
            radius (Optional[Union[str, int]]): Corner radius.
            required (Optional[bool]): Mark as required.
            resize (Optional[str]): CSS resize behavior.
            value (Optional[str]): Current value.
            kwargs: Additional props to set.

        Returns:
            Optional[str]: Current value.
        """
        return self._x_input(
            "textarea",
            key or self._new_widget_id("textarea", label),
            autosize=autosize,
            description=description,
            disabled=disabled,
            error=error,
            inputSize=input_size,
            label=label,
            maxRows=max_rows,
            minRows=min_rows,
            on_change=on_change,
            radius=radius,
            required=required,
            resize=resize,
            value=value,
            **kwargs,
        )

    def autocomplete(
        self,
        label: str,
        data: list[Union[str, GroupOption]],
        *,
        auto_select_on_blur: Optional[bool] = None,
        clear_button_props: Optional[dict[str, Any]] = None,
        clearable: Optional[bool] = None,
        combobox_props: Optional[dict[str, Any]] = None,
        default_drowndown_open: Optional[bool] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        dropdown_opened: Optional[bool] = None,
        error: Optional[str] = None,
        key: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        limit: Optional[int] = None,
        on_change: Optional[Callable[[str], None]] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        value: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Autocomplete text input with suggestions dropdown.

        Args:
            label (str): Field label.
            data (list[Union[str, GroupOption]]): Options and groups.
            auto_select_on_blur (Optional[bool]): Auto select highlighted option on blur.
            clear_button_props (Optional[dict[str, Any]]): Props for clear button.
            clearable (Optional[bool]): Enable clear button.
            combobox_props (Optional[dict[str, Any]]): Props for combobox.
            default_drowndown_open (Optional[bool]): Open dropdown by default.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            dropdown_opened (Optional[bool]): Control dropdown visibility.
            error (Optional[str]): Error message.
            key (Optional[str]): Explicit element key.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            limit (Optional[int]): Max number of options shown.
            on_change (Optional[Callable[[str], None]]): Change handler.
            radius (Optional[Union[str, int]]): Corner radius.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            value (Optional[str]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            kwargs: Additional props to set.

        Returns:
            Optional[str]: Current value.
        """
        return self._x_input(
            "autocomplete",
            key or self._new_widget_id("autocomplete", label),
            autoSelectOnBlur=auto_select_on_blur,
            clearButtonProps=clear_button_props,
            clearable=clearable,
            comboboxProps=combobox_props,
            data=data,
            defaultDropdownOpen=default_drowndown_open,
            description=description,
            disabled=disabled,
            dropdownOpened=dropdown_opened,
            error=error,
            label=label,
            leftSection=left_section,
            leftSectionProps=left_section_props,
            leftSectionWidth=left_section_width,
            limit=limit,
            on_change=on_change,
            radius=radius,
            required=required,
            rightSection=right_section,
            rightSectionProps=right_section_props,
            rightSectionWidth=right_section_width,
            size=size,
            value=value,
            withAsterisk=with_asterisk,
            **kwargs,
        )

    def multiselect(
        self,
        label: str,
        data: list[Union[RLOption, str]],
        *,
        check_icon_position: Optional[Literal["left", "right"]] = None,
        chevron_color: Optional[str] = None,
        clear_button_props: Optional[dict[str, Any]] = None,
        clearable: Optional[bool] = None,
        combobox_props: Optional[dict[str, Any]] = None,
        default_dropdown_opened: Optional[bool] = None,
        default_search_value: Optional[str] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        dropdown_opened: Optional[bool] = None,
        error: Optional[str] = None,
        error_props: Optional[dict[str, Any]] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        hidden_input_props: Optional[dict[str, Any]] = None,
        hidden_input_values_divider: Optional[str] = None,
        hide_picked_options: Optional[bool] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        key: Optional[str] = None,
        label_props: Optional[dict[str, Any]] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        limit: Optional[int] = None,
        max_dropdown_height: Optional[Union[str, int]] = None,
        max_values: Optional[int] = None,
        nothing_found_message: Optional[str] = None,
        on_change: Optional[Callable[[list[str]], None]] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        scroll_area_props: Optional[dict[str, Any]] = None,
        search_value: Optional[str] = None,
        searchable: Optional[bool] = None,
        select_first_option_on_change: Optional[bool] = None,
        size: Optional[str] = None,
        value: Optional[list[str]] = None,
        with_asterisk: Optional[bool] = None,
        with_check_icon: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_scroll_area: Optional[bool] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Multi-select input with search and tags.

        Args:
            label (str): Field label.
            data (list[Union[RLOption, str]]): Available options.
            check_icon_position (Optional[Literal["left", "right"]]): Check icon position.
            chevron_color (Optional[str]): Chevron color.
            clear_button_props (Optional[dict[str, Any]]): Clear button props.
            clearable (Optional[bool]): Enable clear button.
            combobox_props (Optional[dict[str, Any]]): Combobox props.
            default_dropdown_opened (Optional[bool]): Open dropdown by default.
            default_search_value (Optional[str]): Initial search value.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            dropdown_opened (Optional[bool]): Control dropdown visibility.
            error (Optional[str]): Error message.
            error_props (Optional[dict[str, Any]]): Error message props.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            hidden_input_props (Optional[dict[str, Any]]): Hidden input props.
            hidden_input_values_divider (Optional[str]): Divider for hidden input.
            hide_picked_options (Optional[bool]): Hide already selected options.
            input_size (Optional[str]): Control size.
            input_wrapper_order (Optional[list[str]]): Order of input wrapper parts.
            key (Optional[str]): Explicit element key.
            label_props (Optional[dict[str, Any]]): Label props.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            limit (Optional[int]): Max number of options shown.
            max_dropdown_height (Optional[Union[str, int]]): Max dropdown height.
            max_values (Optional[int]): Max number of selected values.
            nothing_found_message (Optional[str]): Message when search returns no results.
            on_change (Optional[Callable[[list[str]], None]]): Change handler.
            radius (Optional[Union[str, int]]): Corner radius.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            scroll_area_props (Optional[dict[str, Any]]): Scroll area props.
            search_value (Optional[str]): Current search value.
            searchable (Optional[bool]): Enable search.
            select_first_option_on_change (Optional[bool]): Auto select first option when changed.
            size (Optional[str]): Control size.
            value (Optional[list[str]]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            with_check_icon (Optional[bool]): Show check icon next to selected options.
            with_error_styles (Optional[bool]): Apply error styles.
            with_scroll_area (Optional[bool]): Wrap dropdown with scroll area.
            kwargs: Additional props to set.

        Returns:
            list[str]: Selected values.
        """
        return self._x_checkbox_group(
            "multiselect",
            key or self._new_widget_id("multiselect", label),
            checkIconPosition=check_icon_position,
            chevronColor=chevron_color,
            clearButtonProps=clear_button_props,
            clearable=clearable,
            comboboxProps=combobox_props,
            defaultDropdownOpened=default_dropdown_opened,
            defaultSearchValue=default_search_value,
            description=description,
            disabled=disabled,
            dropdownOpened=dropdown_opened,
            error=error,
            errorProps=error_props,
            format_func=format_func,
            hiddenInputProps=hidden_input_props,
            hiddenInputValuesDivider=hidden_input_values_divider,
            hidePickedOptions=hide_picked_options,
            inputSize=input_size,
            inputWrapperOrder=input_wrapper_order,
            label=label,
            labelProps=label_props,
            leftSection=left_section,
            leftSectionProps=left_section_props,
            leftSectionWidth=left_section_width,
            limit=limit,
            maxDropdownHeight=max_dropdown_height,
            maxValues=max_values,
            nothingFoundMessage=nothing_found_message,
            on_change=on_change,
            options=data,  # type: ignore[arg-type]
            options_attr="data",
            radius=radius,
            required=required,
            scrollAreaProps=scroll_area_props,
            rightSection=right_section,
            rightSectionProps=right_section_props,
            rightSectionWidth=right_section_width,
            searchValue=search_value,
            searchable=searchable,
            selectFirstOptionOnChange=select_first_option_on_change,
            size=size,
            value=value,
            withAsterisk=with_asterisk,
            withCheckIcon=with_check_icon,
            withErrorStyles=with_error_styles,
            withScrollArea=with_scroll_area,
            **kwargs,
        )

    def select(  # type: ignore[override]
        self,
        label: str,
        options: list[Union[RLOption, str]],
        *,
        allow_deselect: Optional[bool] = None,
        auto_select_on_blur: Optional[bool] = None,
        check_icon_position: Optional[Literal["left", "right"]] = None,
        chevron_color: Optional[str] = None,
        clearable: Optional[bool] = None,
        combobox_props: Optional[dict[str, Any]] = None,
        default_dropdown_opened: Optional[bool] = None,
        default_search_value: Optional[str] = None,
        description: Optional[str] = None,
        error: Optional[str] = None,
        format_func: Optional[Callable[[Any], str]] = None,
        hidden_input_props: Optional[dict[str, Any]] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        key: Optional[str] = None,
        label_props: Optional[dict[str, Any]] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        limit: Optional[int] = None,
        max_dropdown_height: Optional[Union[str, int]] = None,
        nothing_found_message: Optional[str] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        pointer: Optional[bool] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        scroll_area_props: Optional[dict[str, Any]] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        value: Optional[Any] = None,
        with_asterisk: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_scroll_area: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Single-select input with search and advanced features.

        Args:
            label (str): Field label.
            options (list[Union[RLOption, str]]): Available options.
            allow_deselect (Optional[bool]): Allow clearing the selection.
            auto_select_on_blur (Optional[bool]): Auto select highlighted option on blur.
            check_icon_position (Optional[Literal["left", "right"]]): Check icon position.
            chevron_color (Optional[str]): Chevron color.
            clearable (Optional[bool]): Enable clear button.
            combobox_props (Optional[dict[str, Any]]): Combobox props.
            default_dropdown_opened (Optional[bool]): Open dropdown by default.
            default_search_value (Optional[str]): Initial search value.
            description (Optional[str]): Helper text under the label.
            error (Optional[str]): Error message.
            format_func (Optional[Callable[[Any], str]]): Map option value to label.
            hidden_input_props (Optional[dict[str, Any]]): Hidden input props.
            input_size (Optional[str]): Control size.
            input_wrapper_order (Optional[list[str]]): Order of input wrapper parts.
            key (Optional[str]): Explicit element key.
            label_props (Optional[dict[str, Any]]): Label props.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            limit (Optional[int]): Max number of options shown.
            max_dropdown_height (Optional[Union[str, int]]): Max dropdown height.
            nothing_found_message (Optional[str]): Message when search returns no results.
            on_change (Optional[Callable[[Any], None]]): Change handler.
            pointer (Optional[bool]): Use pointer cursor.
            radius (Optional[Union[str, int]]): Corner radius.
            required (Optional[bool]): Mark as required.
            scroll_area_props (Optional[dict[str, Any]]): Scroll area props.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            value (Optional[Any]): Current value.
            with_asterisk (Optional[bool]): Show required asterisk.
            with_error_styles (Optional[bool]): Apply error styles.
            with_scroll_area (Optional[bool]): Wrap dropdown with scroll area.
            kwargs: Additional props to set.

        Returns:
            Any: Selected value.
        """
        return self._x_radio_select(
            "select",
            key or self._new_widget_id("select", label),
            options=options,  # type: ignore[arg-type]
            options_attr="data",
            value=value,
            on_change=on_change,
            format_func=format_func,
            label=label,
            allowDeselect=allow_deselect,
            autoSelectOnBlur=auto_select_on_blur,
            checkIconPosition=check_icon_position,
            chevronColor=chevron_color,
            clearable=clearable,
            comboboxProps=combobox_props,
            defaultDropdownOpened=default_dropdown_opened,
            defaultSearchValue=default_search_value,
            description=description,
            error=error,
            hiddenInputProps=hidden_input_props,
            inputSize=input_size,
            inputWrapperOrder=input_wrapper_order,
            labelProps=label_props,
            leftSection=left_section,
            leftSectionProps=left_section_props,
            leftSectionWidth=left_section_width,
            limit=limit,
            maxDropdownHeight=max_dropdown_height,
            nothingFoundMessage=nothing_found_message,
            pointer=pointer,
            radius=radius,
            rightSection=right_section,
            rightSectionProps=right_section_props,
            rightSectionWidth=right_section_width,
            required=required,
            scrollAreaProps=scroll_area_props,
            size=size,
            withAsterisk=with_asterisk,
            withErrorStyles=with_error_styles,
            withScrollArea=with_scroll_area,
            **kwargs,
        )

    def tags_input(
        self,
        label: str,
        data: list[Union[RLOption, GroupOption, str]],
        *,
        accept_value_on_blur: Optional[bool] = None,
        allow_duplicates: Optional[bool] = None,
        clear_button_props: Optional[dict[str, Any]] = None,
        clearable: Optional[bool] = None,
        combobox_props: Optional[dict[str, Any]] = None,
        default_dropdown_opened: Optional[bool] = None,
        default_search_value: Optional[str] = None,
        description: Optional[str] = None,
        description_props: Optional[dict[str, Any]] = None,
        disabled: Optional[bool] = None,
        dropdown_opened: Optional[bool] = None,
        error: Optional[str] = None,
        error_props: Optional[dict[str, Any]] = None,
        hidden_input_props: Optional[dict[str, Any]] = None,
        hidden_input_values_divider: Optional[str] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        key: Optional[str] = None,
        label_props: Optional[dict[str, Any]] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        limit: Optional[int] = None,
        max_dropdown_height: Optional[Union[str, int]] = None,
        max_tags: Optional[int] = None,
        on_change: Optional[Callable[[list[str]], None]] = None,
        pointer: Optional[bool] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        right_section: Optional[str] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        scroll_area_props: Optional[dict[str, Any]] = None,
        search_value: Optional[str] = None,
        select_first_option_on_change: Optional[bool] = None,
        size: Optional[str] = None,
        split_chars: Optional[list[str]] = None,
        value: Optional[list[str]] = None,
        with_asterisk: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_scroll_area: Optional[bool] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Free-form tags input with autocomplete suggestions.

        Allows typing new tags and selecting from provided options. Supports grouping
        of options and various UI customizations.

        Args:
            label (str): Field label.
            data (list[Union[RLOption, GroupOption, str]]): Available options and/or groups.
            accept_value_on_blur (Optional[bool]): Add current value on blur.
            allow_duplicates (Optional[bool]): Allow duplicate tags.
            clear_button_props (Optional[dict[str, Any]]): Props for the clear button.
            clearable (Optional[bool]): Show clear button to remove all values.
            combobox_props (Optional[dict[str, Any]]): Props passed to the underlying combobox.
            default_dropdown_opened (Optional[bool]): Initial dropdown state.
            default_search_value (Optional[str]): Initial search query.
            description (Optional[str]): Helper text under the label.
            description_props (Optional[dict[str, Any]]): Props for the description element.
            disabled (Optional[bool]): Disable input interaction.
            dropdown_opened (Optional[bool]): Controlled dropdown open state.
            error (Optional[str]): Error message.
            error_props (Optional[dict[str, Any]]): Props for the error element.
            hidden_input_props (Optional[dict[str, Any]]): Props for the hidden form input.
            hidden_input_values_divider (Optional[str]): Divider for hidden input serialization.
            input_size (Optional[str]): Input size variant.
            input_wrapper_order (Optional[list[str]]): Order of input wrapper parts.
            key (Optional[str]): Explicit element key.
            label_props (Optional[dict[str, Any]]): Props for the label element.
            left_section (Optional[RouteLitElement]): Left section content.
            left_section_props (Optional[dict[str, Any]]): Props for the left section wrapper.
            left_section_width (Optional[str]): Width of the left section.
            limit (Optional[int]): Max number of items displayed in dropdown.
            max_dropdown_height (Optional[Union[str, int]]): Max height of the dropdown.
            max_tags (Optional[int]): Max number of tags that can be added.
            on_change (Optional[Callable[[list[str]], None]]): Change handler.
            pointer (Optional[bool]): Show pointer cursor on hover.
            radius (Optional[Union[str, int]]): Corner radius.
            required (Optional[bool]): Mark field as required.
            right_section (Optional[str]): Right section content.
            right_section_props (Optional[dict[str, Any]]): Props for the right section wrapper.
            right_section_width (Optional[str]): Width of the right section.
            scroll_area_props (Optional[dict[str, Any]]): Props for dropdown scroll area.
            search_value (Optional[str]): Controlled search query value.
            select_first_option_on_change (Optional[bool]): Auto-select first option on change.
            size (Optional[str]): Control size.
            split_chars (Optional[list[str]]): Characters that split input into tags.
            value (Optional[list[str]]): Current value (list of tags).
            with_asterisk (Optional[bool]): Show required asterisk.
            with_error_styles (Optional[bool]): Apply error styles when error is set.
            with_scroll_area (Optional[bool]): Wrap dropdown list in a scroll area.
            kwargs: Additional props to set.

        Returns:
            list[str]: Current list of tags.
        """
        return cast(
            list[str],
            self._x_checkbox_group(
                "tagsinput",
                key or self._new_widget_id("tagsinput", label),
                acceptValueOnBlur=accept_value_on_blur,
                allowDuplicates=allow_duplicates,
                clearButtonProps=clear_button_props,
                clearable=clearable,
                comboboxProps=combobox_props,
                defaultDropdownOpened=default_dropdown_opened,
                defaultSearchValue=default_search_value,
                description=description,
                descriptionProps=description_props,
                disabled=disabled,
                dropdownOpened=dropdown_opened,
                error=error,
                errorProps=error_props,
                hiddenInputProps=hidden_input_props,
                hiddenInputValuesDivider=hidden_input_values_divider,
                inputSize=input_size,
                inputWrapperOrder=input_wrapper_order,
                label=label,
                labelProps=label_props,
                leftSection=left_section,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                limit=limit,
                maxDropdownHeight=max_dropdown_height,
                maxTags=max_tags,
                on_change=on_change,
                options=data,  # type: ignore[arg-type]
                options_attr="data",
                pointer=pointer,
                radius=radius,
                required=required,
                rightSection=right_section,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                scrollAreaProps=scroll_area_props,
                searchValue=search_value,
                selectFirstOptionOnChange=select_first_option_on_change,
                size=size,
                splitChars=split_chars,
                value=value,
                withAsterisk=with_asterisk,
                withErrorStyles=with_error_styles,
                withScrollArea=with_scroll_area,
                **kwargs,
            ),
        )

    def action_icon(
        self,
        name: str,
        *,
        key: Optional[str] = None,
        on_click: Optional[Callable[[], None]] = None,
        rl_virtual: Optional[bool] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Icon-only button for compact actions.

        Args:
            name (str): Icon name.
            key (Optional[str]): Explicit element key.
            on_click (Optional[Callable[[], None]]): Click handler.
            rl_virtual (Optional[bool]): Whether the element is virtual.
            kwargs: Additional props to set.

        Returns:
            bool: Click result flag.
        """
        return self._x_button(
            "actionicon",
            key or self._new_widget_id("actionicon", name),
            name=name,
            on_click=on_click,
            rl_virtual=rl_virtual,
            **kwargs,
        )

    def action_icon_group(
        self,
        border_width: Optional[str] = None,
        orientation: Optional[Literal["horizontal", "vertical"]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Group multiple `action_icon` elements together.

        Args:
            border_width (Optional[str]): Border width between icons.
            orientation (Optional[Literal["horizontal", "vertical"]]): Layout direction.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the group element.
        """
        element = self._create_element(
            key=self._new_text_id("actionicongroup"),
            name="actionicongroup",
            props={
                "borderWidth": border_width,
                "orientation": orientation,
                **kwargs,
            },
            virtual=True,
        )
        return cast(RLBuilder, self._build_nested_builder(element))

    def action_icon_group_section(
        self,
        text: Optional[str] = None,
        rl_virtual: bool = True,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Section within an `action_icon_group`, usually for labels or extra content.

        Args:
            text (Optional[str]): Section text.
            rl_virtual (bool): Whether the element is virtual.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the section element.
        """
        element = self._create_element(
            key=self._new_text_id("actionicongroupsection"),
            name="actionicongroupsection",
            props={
                "children": text,
                **kwargs,
            },
            virtual=rl_virtual,
        )
        return self._build_nested_builder(element)  # type: ignore[return-value]

    def button(
        self,
        text: str,
        *,
        color: Optional[str] = None,
        disabled: Optional[bool] = None,
        full_width: Optional[bool] = None,
        gradient: Optional[dict[str, Any]] = None,
        justify: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        loading: Optional[bool] = None,
        key: Optional[str] = None,
        on_click: Optional[Callable[[], None]] = None,
        radius: Optional[Union[str, int]] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        rl_virtual: Optional[bool] = None,
        size: Optional[str] = None,
        variant: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Standard button component.

        Args:
            text (str): Button text.
            color (Optional[str]): Accent color or variant color.
            disabled (Optional[bool]): Disable interaction.
            full_width (Optional[bool]): Make button take full width.
            gradient (Optional[dict[str, Any]]): Gradient configuration for variant.
            justify (Optional[str]): Content justification.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            loading (Optional[bool]): Show loading state.
            key (Optional[str]): Explicit element key.
            on_click (Optional[Callable[[], None]]): Click handler.
            radius (Optional[Union[str, int]]): Corner radius.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            rl_virtual (Optional[bool]): Whether the element is virtual.
            size (Optional[str]): Control size.
            variant (Optional[str]): Visual variant.
            kwargs: Additional props to set.

        Returns:
            bool: Click result flag.
        """
        return self._x_button(
            "button",
            text,
            on_click=on_click,
            rl_virtual=rl_virtual,
            color=color,
            disabled=disabled,
            fullWidth=full_width,
            gradient=gradient,
            justify=justify,
            key=key or self._new_widget_id("button", text),
            leftSection=left_section,
            leftSectionProps=left_section_props,
            leftSectionWidth=left_section_width,
            loading=loading,
            radius=radius,
            rightSection=right_section,
            rightSectionProps=right_section_props,
            rightSectionWidth=right_section_width,
            size=size,
            variant=variant,
            **kwargs,
        )

    @staticmethod
    def icon(name: str, **kwargs: Any) -> RouteLitElement:
        """
        Create an icon element to be used as an adornment.

        Args:
            name (str): Icon name.
            kwargs: Additional props to set.

        Returns:
            RouteLitElement: Virtual icon element.
        """
        return RouteLitElement(
            name="icon",
            key="",
            props={
                "name": name,
                **kwargs,
            },
            virtual=True,
        )

    def anchor(
        self,
        href: str,
        text: str,
        *,
        c: Optional[str] = None,
        gradient: Optional[dict[str, Any]] = None,
        inherit: Optional[bool] = None,
        inline: Optional[bool] = None,
        is_external: bool = False,
        line_clamp: Optional[int] = None,
        replace: bool = False,
        size: Optional[str] = None,
        truncate: Optional[str] = None,
        underline: Optional[str] = None,
        variant: Optional[str] = None,
        **kwargs: Any,
    ) -> RouteLitElement:
        """
        Anchor link element that routes internally or opens external URLs.

        Args:
            href (str): Destination path or URL.
            text (str): Link text.
            c (Optional[str]): Text color.
            gradient (Optional[dict[str, Any]]): Gradient style.
            inherit (Optional[bool]): Inherit parent font styles.
            inline (Optional[bool]): Render inline.
            is_external (bool): Open in a new tab/window if true.
            line_clamp (Optional[int]): Clamp to a number of lines.
            replace (bool): Replace history entry when routing.
            size (Optional[str]): Text size.
            truncate (Optional[str]): Truncate overflow.
            underline (Optional[str]): Underline style.
            variant (Optional[str]): Visual variant.
            kwargs: Additional props to set.

        Returns:
            RouteLitElement: Configured anchor element.
        """
        return self.link(
            href,
            text,
            c=c,
            rl_element_type="anchor",
            gradient=gradient,
            is_external=is_external,
            inherit=inherit,
            inline=inline,
            lineClamp=line_clamp,
            replace=replace,
            size=size,
            truncate=truncate,
            underline=underline,
            variant=variant,
            **kwargs,
        )

    def nav_link(
        self,
        href: str,
        label: str,
        *,
        active: Optional[bool] = None,
        auto_contrast: Optional[bool] = None,
        children_offset: Optional[str] = None,
        color: Optional[str] = None,
        default_opened: Optional[bool] = None,
        description: Optional[str] = None,
        disable_right_section_rotation: Optional[bool] = None,
        disabled: Optional[bool] = None,
        exact: Optional[bool] = None,
        is_external: bool = False,
        left_section: Optional[RouteLitElement] = None,
        no_wrap: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Navigation link, typically used in sidebars or menus.

        Args:
            href (str): Destination path.
            label (str): Visible label.
            active (Optional[bool]): Force active state.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            children_offset (Optional[str]): Indentation for children links.
            color (Optional[str]): Accent color.
            default_opened (Optional[bool]): Start expanded.
            description (Optional[str]): Helper text under the label.
            disable_right_section_rotation (Optional[bool]): Disable chevron rotation.
            disabled (Optional[bool]): Disable interaction.
            exact (Optional[bool]): Match route exactly.
            is_external (bool): Treat as external link.
            left_section (Optional[RouteLitElement]): Left adornment.
            no_wrap (Optional[bool]): Prevent label wrapping.
            right_section (Optional[RouteLitElement]): Right adornment.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder for child links/content.
        """
        element = self.link(
            href,
            label,
            active=active,
            autoContrast=auto_contrast,
            childrenOffset=children_offset,
            color=color,
            defaultOpened=default_opened,
            description=description,
            disableRightSectionRotation=disable_right_section_rotation,
            disabled=disabled,
            exact=exact,
            is_external=is_external,
            leftSection=left_section,
            noWrap=no_wrap,
            rightSection=right_section,
            rl_element_type="navlink",
            rl_text_attr="label",
            **kwargs,
        )
        return self._build_nested_builder(element)  # type: ignore[return-value]

    def tabs(
        self,
        tabs: list[Union[MTTab, str]],
        *,
        activate_tab_with_keyboard: Optional[bool] = None,
        allow_tab_deactivation: Optional[bool] = None,
        auto_contrast: Optional[bool] = None,
        color: Optional[str] = None,
        default_value: Optional[str] = None,
        inverted: Optional[bool] = None,
        keep_mounted: Optional[bool] = None,
        key: Optional[str] = None,
        loop: Optional[bool] = None,
        orientation: Optional[Literal["horizontal", "vertical"]] = None,
        placement: Optional[Literal["left", "right"]] = None,
        radius: Optional[Union[str, int]] = None,
        tablist_grow: Optional[bool] = None,
        tablist_justify: Optional[str] = None,
        variant: Optional[Literal["default", "outline", "pills"]] = None,
        **kwargs: Any,
    ) -> tuple["RLBuilder", ...]:
        """
        Tabs component with a tablist and corresponding tab panels.

        Args:
            tabs (list[Union[MTTab, str]]): Tabs configuration or values.
            activate_tab_with_keyboard (Optional[bool]): Enable keyboard navigation.
            allow_tab_deactivation (Optional[bool]): Allow deactivating active tab.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            color (Optional[str]): Accent color.
            default_value (Optional[str]): Initially selected tab value.
            inverted (Optional[bool]): Invert styles.
            keep_mounted (Optional[bool]): Keep inactive panels mounted.
            key (Optional[str]): Explicit element key.
            loop (Optional[bool]): Loop focus within tabs.
            orientation (Optional[Literal["horizontal", "vertical"]]): Orientation.
            placement (Optional[Literal["left", "right"]]): Placement of tabs relative to panels.
            radius (Optional[Union[str, int]]): Corner radius.
            tablist_grow (Optional[bool]): Make tablist items grow.
            tablist_justify (Optional[str]): Tablist justification.
            variant (Optional[Literal["default", "outline", "pills"]]): Visual variant.
            kwargs: Additional props to set.

        Returns:
            tuple[RLBuilder, ...]: Panel builders, one per tab value.

        Example:
        ```python
        tab1, tab2 = ui.tabs(
            tabs=[
                ui.tab(value="tab1", label="Tab 1"),
                "Tab 2",
            ],
            default_value="tab1",
            variant="outline",
        )
        with tab1:
            ui.text("Tab body 1")
        with tab2:
            ui.text("Tab body 2")
        ```
        """
        default_value = default_value or (
            (tabs[0]["value"] if isinstance(tabs[0], dict) else tabs[0]) if tabs and len(tabs) > 0 else None
        )
        tabs_root = self._build_nested_builder(
            self._create_element(
                key=key or self._new_text_id("tabs"),
                name="tabs",
                props={
                    "activateTabWithKeyboard": activate_tab_with_keyboard,
                    "allowTabDeactivation": allow_tab_deactivation,
                    "autoContrast": auto_contrast,
                    "color": color,
                    "defaultValue": default_value,
                    "inverted": inverted,
                    "keepMounted": keep_mounted,
                    "loop": loop,
                    "orientation": orientation,
                    "placement": placement,
                    "radius": radius,
                    "variant": variant,
                    **kwargs,
                },
                virtual=True,
            )
        )
        tabs_panels = []
        with tabs_root:
            tab_list = self._build_nested_builder(
                self._create_element(
                    key=self._new_text_id("tablist"),
                    name="tablist",
                    props={
                        "grow": tablist_grow,
                        "justify": tablist_justify,
                    },
                    virtual=True,
                )
            )
            for tab in tabs:
                tab_props = {"value": tab} if isinstance(tab, str) else tab
                keep_mounted_val = tab_props.pop("keep_mounted", None)
                keep_mounted = keep_mounted_val if isinstance(keep_mounted_val, (bool, type(None))) else None
                left_section = tab_props.pop("left_section", None)
                right_section = tab_props.pop("right_section", None)
                label = tab_props.pop("label", None)
                tab_props["children"] = label or tab_props["value"]
                if left_section:
                    tab_props["leftSection"] = left_section  # type: ignore[assignment, arg-type]
                if right_section:
                    tab_props["rightSection"] = right_section  # type: ignore[assignment, arg-type]
                with tab_list:
                    self._create_element(
                        key=self._new_text_id("tab"),
                        name="tab",
                        props=tab_props,  # type: ignore[arg-type]
                        virtual=True,
                    )
                tabs_panels.append(
                    self._build_nested_builder(
                        self._create_element(
                            key=self._new_text_id("tabpanel"),
                            name="tabpanel",
                            props={
                                "value": tab_props["value"],
                                "keepMounted": keep_mounted,
                            },
                            virtual=True,
                        )
                    )
                )
        return tuple(tabs_panels)  # type: ignore[arg-type]

    @staticmethod
    def tab(
        value: str,
        label: Optional[str] = None,
        color: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        right_section: Optional[RouteLitElement] = None,
        size: Optional[Union[str, int]] = None,
        keep_mounted: Optional[bool] = None,
        **kwargs: Any,
    ) -> MTTab:
        """
        Helper to create an `MTTab` configuration object.
        Used to describe the props for each tab in the `tabs` function.

        Args:
            value (str): Tab value.
            label (Optional[str]): Tab label.
            color (Optional[str]): Accent color.
            left_section (Optional[RouteLitElement]): Left adornment for tab.
            right_section (Optional[RouteLitElement]): Right adornment for tab.
            size (Optional[Union[str, int]]): Size for the tab.
            keep_mounted (Optional[bool]): Keep panel mounted when inactive.
            kwargs: Additional props to set.

        Returns:
            MTTab: Tab configuration object.
        """
        return MTTab(  # type: ignore[no-any-return]
            value=value,
            label=label,
            color=color,
            left_section=left_section,
            right_section=right_section,
            size=size,
            keep_mounted=keep_mounted,
            **kwargs,  # type: ignore[typeddict-item]
        )

    def alert(
        self,
        title: str,
        *,
        auto_contrast: Optional[bool] = None,
        key: Optional[str] = None,
        color: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        icon: Optional[RouteLitElement] = None,
        with_close_button: Optional[bool] = None,
        close_button_label: Optional[str] = None,
        on_close: Optional[Callable[[], bool]] = None,
        variant: Optional[Literal["default", "filled", "light", "outline", "white", "transparent"]] = None,
        text: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Inline alert with optional icon and close button.

        Args:
            title (str): Alert title.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            key (Optional[str]): Explicit element key.
            color (Optional[str]): Color variant.
            radius (Optional[Union[str, int]]): Corner radius.
            icon (Optional[RouteLitElement]): Leading icon.
            with_close_button (Optional[bool]): Show close button.
            close_button_label (Optional[str]): Accessible label for close button.
            on_close (Optional[Callable[[], bool]]): Close handler.
            variant (Optional[Literal["default", "filled", "light", "outline", "white", "transparent"]]): Visual variant.
            text (Optional[str]): Alert content.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the alert element.
        """
        return self._x_dialog(  # type: ignore[return-value]
            "alert",
            key or self._new_widget_id("alert", title),
            autoContrast=auto_contrast,
            closeButtonLabel=close_button_label,
            color=color,
            radius=radius,
            icon=icon,
            title=title,
            on_close=on_close,
            variant=variant,
            withCloseButton=with_close_button,
            children=text,
            **kwargs,
        )

    def notification(
        self,
        title: str,
        *,
        key: Optional[str] = None,
        close_button_props: Optional[dict[str, Any]] = None,
        color: Optional[str] = None,
        icon: Optional[RouteLitElement] = None,
        on_close: Optional[Callable[[], bool]] = None,
        radius: Optional[Union[str, int]] = None,
        text: Optional[str] = None,
        with_border: Optional[bool] = None,
        with_close_button: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Notification element for transient messages.

        Args:
            title (str): Notification title.
            key (Optional[str]): Explicit element key.
            close_button_props (Optional[dict[str, Any]]): Close button props.
            color (Optional[str]): Color variant.
            icon (Optional[RouteLitElement]): Leading icon.
            on_close (Optional[Callable[[], bool]]): Close handler.
            radius (Optional[Union[str, int]]): Corner radius.
            text (Optional[str]): Notification content.
            with_border (Optional[bool]): Show border.
            with_close_button (Optional[bool]): Show close button.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the notification element.
        """
        return self._x_dialog(  # type: ignore[return-value]
            "notification",
            key or self._new_widget_id("notification", title),
            closeButtonProps=close_button_props,
            color=color,
            radius=radius,
            icon=icon,
            title=title,
            on_close=on_close,
            withBorder=with_border,
            withCloseButton=with_close_button,
            children=text,
            **kwargs,
        )

    def progress(
        self,
        value: float,
        *,
        key: Optional[str] = None,
        animated: Optional[bool] = None,
        auto_contrast: Optional[bool] = None,
        color: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        size: Optional[Union[str, int]] = None,
        striped: Optional[bool] = None,
        transition_duration: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Determinate progress bar.

        Args:
            value (float): Progress value from 0 to 100.
            key (Optional[str]): Explicit element key.
            animated (Optional[bool]): Animate stripes.
            auto_contrast (Optional[bool]): Improve contrast automatically.
            color (Optional[str]): Color variant.
            radius (Optional[Union[str, int]]): Corner radius.
            size (Optional[Union[str, int]]): Height of the bar.
            striped (Optional[bool]): Show stripes.
            transition_duration (Optional[int]): Animation duration in ms.
            kwargs: Additional props to set.
        """
        self._create_element(
            key=key or self._new_text_id("progress"),
            name="progress",
            props={
                "value": value,
                "animated": animated,
                "autoContrast": auto_contrast,
                "color": color,
                "radius": radius,
                "size": size,
                "striped": striped,
                "transitionDuration": transition_duration,
                **kwargs,
            },
        )

    def dialog(
        self,
        key: Optional[str] = None,
        *,
        with_close_button: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Open a dialog container for arbitrary content.

        Args:
            key (Optional[str]): Explicit element key.
            with_close_button (Optional[bool]): Show close button.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the dialog element.
        """
        return super()._x_dialog(  # type: ignore[return-value]
            "dialog",
            key or self._new_text_id("dialog"),
            opened=True,
            withCloseButton=with_close_button,
            **kwargs,
        )

    def drawer(
        self,
        key: Optional[str] = None,
        *,
        close_button_props: Optional[dict] = None,
        close_on_click_outside: Optional[bool] = None,
        close_on_escape: Optional[bool] = None,
        on_close: Optional[Callable[[], bool]] = None,
        keep_mounted: Optional[bool] = None,
        lock_scroll: Optional[bool] = None,
        offset: Optional[Union[str, int]] = None,
        overlay_props: Optional[dict] = None,
        padding: Optional[Union[str, int]] = None,
        portal_props: Optional[dict] = None,
        position: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        remove_scroll_props: Optional[dict] = None,
        return_focus: Optional[bool] = None,
        scroll_area_component: Optional[str] = None,
        shadow: Optional[str] = None,
        size: Optional[Union[str, int]] = None,
        stack_id: Optional[str] = None,
        title: Optional[str] = None,
        transition_props: Optional[dict] = None,
        trap_focus: Optional[bool] = None,
        with_close_button: Optional[bool] = None,
        with_overlay: Optional[bool] = None,
        within_portal: Optional[bool] = None,
        z_index: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Drawer component that slides from screen edges.

        Args:
            key (Optional[str]): Explicit element key.
            close_button_props (Optional[dict]): Close button props.
            close_on_click_outside (Optional[bool]): Close when clicking outside.
            close_on_escape (Optional[bool]): Close on Escape key.
            on_close (Optional[Callable[[], bool]]): Close handler.
            keep_mounted (Optional[bool]): Keep in DOM when closed.
            lock_scroll (Optional[bool]): Lock document scroll when opened.
            offset (Optional[Union[str, int]]): Offset from viewport edges.
            overlay_props (Optional[dict]): Overlay props.
            padding (Optional[Union[str, int]]): Content padding.
            portal_props (Optional[dict]): Portal props.
            position (Optional[str]): Edge position.
            radius (Optional[Union[str, int]]): Corner radius.
            remove_scroll_props (Optional[dict]): Remove scroll props.
            return_focus (Optional[bool]): Return focus to trigger on close.
            scroll_area_component (Optional[str]): Custom scroll area component.
            shadow (Optional[str]): Shadow preset.
            size (Optional[Union[str, int]]): Drawer size.
            stack_id (Optional[str]): Stack identifier.
            title (Optional[str]): Header title.
            transition_props (Optional[dict]): Transition props.
            trap_focus (Optional[bool]): Trap focus inside drawer.
            with_close_button (Optional[bool]): Show close button.
            with_overlay (Optional[bool]): Show overlay.
            within_portal (Optional[bool]): Render within portal.
            z_index (Optional[Union[str, int]]): CSS z-index.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the drawer element.
        """
        return super()._x_dialog(  # type: ignore[return-value]
            "drawer",
            key or self._new_text_id("drawer"),
            opened=True,
            closeButtonProps=close_button_props,
            closeOnClickOutside=close_on_click_outside,
            closeOnEscape=close_on_escape,
            keepMounted=keep_mounted,
            lockScroll=lock_scroll,
            offset=offset,
            on_close=on_close,
            overlayProps=overlay_props,
            padding=padding,
            portalProps=portal_props,
            position=position,
            radius=radius,
            removeScrollProps=remove_scroll_props,
            returnFocus=return_focus,
            scrollAreaComponent=scroll_area_component,
            shadow=shadow,
            size=size,
            stackId=stack_id,
            title=title,
            transitionProps=transition_props,
            trapFocus=trap_focus,
            withCloseButton=with_close_button,
            withOverlay=with_overlay,
            withinPortal=within_portal,
            zIndex=z_index,
            **kwargs,
        )

    def modal(
        self,
        key: Optional[str] = None,
        *,
        title: Optional[str] = None,
        with_close_button: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Centered modal dialog.

        Args:
            key (Optional[str]): Explicit element key.
            title (Optional[str]): Header title.
            with_close_button (Optional[bool]): Show close button.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the modal element.
        """
        return super()._x_dialog(  # type: ignore[return-value]
            "modal",
            key or self._new_text_id("modal"),
            opened=True,
            title=title,
            withCloseButton=with_close_button,
            **kwargs,
        )

    # override _dialog to use modal instead of dialog
    def _dialog(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Internal helper: open a modal by default when using dialog-like APIs.
        """
        return self.modal(key or self._new_text_id("modal"), **kwargs)

    def affix(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Position an element at a fixed offset from viewport edges.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the affix element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="affix",
            key=key or self._new_text_id("affix"),
            props=kwargs,
            virtual=True,
        )

    def image(
        self,
        src: str,
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Display an image.

        Args:
            src (str): Image source URL.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.
        """
        self._create_element(
            name="image",
            key=key or self._new_widget_id("image", src),
            props={"src": src, **kwargs},
        )

    def number_formatter(
        self,
        value: Union[float, int, str],
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Format and display a number according to given options.

        Args:
            value (Union[float, int, str]): Value to format.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.
        """
        self._create_element(
            key=key or self._new_text_id("numberformatter"),
            name="numberformatter",
            props={"value": value, **kwargs},
        )

    def spoiler(
        self,
        show_label: str = "Show more",
        hide_label: str = "Show less",
        *,
        key: Optional[str] = None,
        initial_state: bool = False,
        max_height: Optional[int] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Collapsible content with show/hide controls.

        Args:
            show_label (str): Label when collapsed.
            hide_label (str): Label when expanded.
            key (Optional[str]): Explicit element key.
            initial_state (bool): Initial expanded state.
            max_height (Optional[int]): Max visible height when collapsed.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the spoiler element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="spoiler",
            key=key or self._new_text_id("spoiler"),
            props={
                "showLabel": show_label,
                "hideLabel": hide_label,
                "initialState": initial_state,
                "maxHeight": max_height,
                **kwargs,
            },
            virtual=True,
        )

    def text(  # type: ignore[override]
        self,
        text: str,
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Render plain text content.

        Args:
            text (str): Text content.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.
        """
        self._create_element(
            name="text",
            key=key or self._new_text_id("text"),
            props={"children": text, **kwargs},
        )

    def title(  # type: ignore[override]
        self,
        text: str,
        *,
        key: Optional[str] = None,
        order: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Title text with semantic order (h1-h6).

        Args:
            text (str): Title content.
            key (Optional[str]): Explicit element key.
            order (Optional[int]): Heading level (1-6).
            kwargs: Additional props to set.
        """
        self._create_element(
            name="title",
            key=key or self._new_text_id("title"),
            props={"children": text, "order": order, **kwargs},
        )

    def table(
        self,
        key: Optional[str] = None,
        *,
        body: Optional[list[list[Any]]] = None,
        caption: Optional[str] = None,
        head: Optional[list[str]] = None,
        foot: Optional[list[str]] = None,
        sticky_header: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Data table with optional head, body, foot and caption.

        Args:
            key (Optional[str]): Explicit element key.
            body (Optional[list[list[Any]]]): Table body rows.
            caption (Optional[str]): Table caption.
            head (Optional[list[str]]): Header row cells.
            foot (Optional[list[str]]): Footer row cells.
            sticky_header (Optional[bool]): Make header sticky when scrolling.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the table element.
        """
        data = {
            "body": body,
            "caption": caption,
            "head": head,
            "foot": foot,
        }
        return self._create_builder_element(  # type: ignore[return-value]
            name="table",
            key=key or self._new_text_id("table"),
            props={"data": data, "stickyHeader": sticky_header, **kwargs},
        )

    def table_caption(
        self,
        text: str,
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Add a caption to the current table.

        Args:
            text (str): Caption text.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.
        """
        self._create_element(
            name="tablecaption",
            key=key or self._new_text_id("tablecaption"),
            props={"children": text, **kwargs},
            virtual=True,
        )

    def table_head(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table head section.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the head section.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablehead",
            key=key or self._new_text_id("tablehead"),
            props=kwargs,
            virtual=True,
        )

    def table_foot(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table foot section.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the foot section.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablefoot",
            key=key or self._new_text_id("tablefoot"),
            props=kwargs,
            virtual=True,
        )

    def table_row(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table row.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the row.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablerow",
            key=key or self._new_text_id("tablerow"),
            props=kwargs,
            virtual=True,
        )

    def table_cell(
        self,
        text: Optional[str] = None,
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table cell.

        Args:
            text (Optional[str]): Cell text content.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the cell.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablecell",
            key=key or self._new_text_id("tablecell"),
            props={"children": text, **kwargs},
            virtual=True,
        )

    def table_header(
        self,
        text: Optional[str] = None,
        *,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table header cell.

        Args:
            text (Optional[str]): Header text content.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the header cell.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tableheader",
            key=key or self._new_text_id("tableheader"),
            props={"children": text, **kwargs},
            virtual=True,
        )

    def table_body(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Create a table body section.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the body section.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablebody",
            key=key or self._new_text_id("tablebody"),
            props=kwargs,
            virtual=True,
        )

    def table_scroll_container(
        self,
        *,
        key: Optional[str] = None,
        max_height: Optional[Union[str, int]] = None,
        max_width: Optional[Union[str, int]] = None,
        min_height: Optional[Union[str, int]] = None,
        min_width: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Scrollable container for large tables.

        Args:
            key (Optional[str]): Explicit element key.
            max_height (Optional[Union[str, int]]): Maximum height.
            max_width (Optional[Union[str, int]]): Maximum width.
            min_height (Optional[Union[str, int]]): Minimum height.
            min_width (Optional[Union[str, int]]): Minimum width.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the scroll container.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="tablescrollcontainer",
            key=key or self._new_text_id("tablescrollcontainer"),
            props={
                "maxHeight": max_height,
                "maxWidth": max_width,
                "minHeight": min_height,
                "minWidth": min_width,
                **kwargs,
            },
            virtual=True,
        )

    def box(
        self,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Generic layout container.

        Args:
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the box element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="box",
            key=key or self._new_text_id("box"),
            props=kwargs,
            virtual=True,
        )

    def paper(
        self,
        *,
        key: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        shadow: Optional[str] = None,
        with_border: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Container with background, border, and shadow.

        Args:
            key (Optional[str]): Explicit element key.
            radius (Optional[Union[str, int]]): Corner radius.
            shadow (Optional[str]): Shadow preset.
            with_border (Optional[bool]): Show border.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the paper element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="paper",
            key=key or self._new_text_id("paper"),
            props={
                "radius": radius,
                "shadow": shadow,
                "withBorder": with_border,
                **kwargs,
            },
            virtual=True,
        )

    def scroll_area(
        self,
        *,
        key: Optional[str] = None,
        offset_scrollbars: Optional[Union[bool, Literal["x", "y", "present"]]] = None,
        overscroll_behavior: Optional[str] = None,
        scroll_hide_delay: Optional[int] = None,
        scrollbar_size: Optional[Union[str, int]] = None,
        scrollbars: Optional[Union[bool, Literal["x", "y", "xy"]]] = None,
        type: Optional[Literal["auto", "scroll", "always", "hover", "never"]] = None,  # noqa: A002
        viewport_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Scrollable area with configurable scrollbars and behavior.

        Args:
            key (Optional[str]): Explicit element key.
            offset_scrollbars (Optional[Union[bool, Literal["x", "y", "present"]]): Offset scrollbars from content.
            overscroll_behavior (Optional[str]): CSS overscroll behavior.
            scroll_hide_delay (Optional[int]): Delay before hiding scrollbars.
            scrollbar_size (Optional[Union[str, int]]): Scrollbar size.
            scrollbars (Optional[Union[bool, Literal["x", "y", "xy"]]): Which axes show scrollbars.
            type (Optional[Literal["auto", "scroll", "always", "hover", "never"]]): Scrollbar visibility policy.
            viewport_props (Optional[dict[str, Any]]): Viewport element props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the scroll area.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="scrollarea",
            key=key or self._new_text_id("scrollarea"),
            props={
                "offsetScrollbars": offset_scrollbars,
                "overscrollBehavior": overscroll_behavior,
                "scrollHideDelay": scroll_hide_delay,
                "scrollbarSize": scrollbar_size,
                "scrollbars": scrollbars,
                "type": type,
                "viewportProps": viewport_props,
                **kwargs,
            },
            virtual=True,
        )

    def accordion(
        self,
        value: Optional[Union[list[str], str]] = None,
        *,
        key: Optional[str] = None,
        chevron: Optional[Any] = None,
        chevron_icon_size: Optional[Union[str, int]] = None,
        chevron_position: Optional[str] = None,
        chevron_size: Optional[Union[str, int]] = None,
        disable_chevron_rotation: Optional[bool] = None,
        loop: Optional[bool] = None,
        multiple: Optional[bool] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        order: Optional[Literal[2, 3, 4, 5, 6]] = None,
        radius: Optional[Union[str, int]] = None,
        transition_duration: Optional[int] = None,
        variant: Optional[Literal["default", "filled", "separated", "contained", "unstyled"]] = None,
    ) -> "RLBuilder":
        """
        Accordion component.

        Args:
            value (Optional[Union[list[str], str]]): Controlled component value.
            key (Optional[str]): Unique key for the component.
            chevron (Optional[Any]): Custom chevron icon.
            chevron_icon_size (Optional[Union[str, int]]): Size of default chevron icon.
            chevron_position (Optional[str]): Position of chevron relative to label.
            chevron_size (Optional[Union[str, int]]): Size of chevron icon container.
            disable_chevron_rotation (Optional[bool]): Disable chevron rotation.
            loop (Optional[bool]): Loop through items with arrow keys.
            multiple (Optional[bool]): Allow multiple items open at once.
            on_change (Optional[Callable[[Any], None]]): Called when value changes.
            order (Optional[Literal[2,3,4,5,6]]): Heading order.
            radius (Optional[Union[str, int]]): Border radius.
            transition_duration (Optional[int]): Transition duration in ms.
            variant (Optional[Literal["default", "filled", "separated", "contained", "unstyled"]]): Visual variant.

        Returns:
            RLBuilder: A nested builder scoped to the accordion.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="accordion",
            key=key or self._new_text_id("accordion"),
            props={
                "defaultValue": value,
                "chevron": chevron,
                "chevronIconSize": chevron_icon_size,
                "chevronPosition": chevron_position,
                "chevronSize": chevron_size,
                "disableChevronRotation": disable_chevron_rotation,
                "loop": loop,
                "multiple": multiple,
                "onChange": on_change,
                "order": order,
                "radius": radius,
                "transitionDuration": transition_duration,
                "variant": variant,
            },
            virtual=True,
        )

    def accordion_item(
        self,
        label: str,
        *,
        key: Optional[str] = None,
        chevron: Optional[RouteLitElement] = None,
        disabled: Optional[bool] = None,
        icon: Optional[RouteLitElement] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Accordion item component.
        """
        item_key = self._new_widget_id("accordionitem", label) if key is None else key
        accordion_item = self._create_builder_element(
            name="accordionitem",
            key=item_key,
            props={
                "value": item_key,
                **kwargs,
            },
            virtual=True,
        )
        with accordion_item:
            control_key = self._new_widget_id("accordioncontrol", label) if key is None else key + "-control"
            self._create_element(
                "accordioncontrol",
                key=control_key,
                props={
                    "chevron": chevron,
                    "disabled": disabled,
                    "icon": icon,
                    "children": label,
                },
                virtual=True,
            )
            panel_key = self._new_widget_id("accordionpanel", label) if key is None else key + "-panel"
            panel = self._create_builder_element(
                name="accordionpanel",
                key=panel_key,
                props={},
                virtual=True,
            )
            return panel  # type: ignore[return-value]

    def expander(
        self,
        title: str,
        *,
        is_open: Optional[bool] = None,
        key: Optional[str] = None,
        chevron: Optional[Any] = None,
        chevron_icon_size: Optional[Union[str, int]] = None,
        chevron_position: Optional[str] = None,
        chevron_size: Optional[Union[str, int]] = None,
        disabled: Optional[bool] = None,
        disable_chevron_rotation: Optional[bool] = None,
        icon: Optional[RouteLitElement] = None,
        radius: Optional[Union[str, int]] = None,
        transition_duration: Optional[int] = None,
        variant: Optional[Literal["default", "filled", "separated", "contained", "unstyled"]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Expander component.
        This is a wrapper around the accordion component.

        Args:
            title (str): Title text shown in the expander header
            is_open (Optional[bool]): Whether the expander is initially expanded
            key (Optional[str]): Unique key for the component
            chevron (Optional[Any]): Custom chevron element
            chevron_icon_size (Optional[Union[str, int]]): Size of the chevron icon
            chevron_position (Optional[str]): Position of the chevron icon
            chevron_size (Optional[Union[str, int]]): Size of the chevron container
            disabled (Optional[bool]): Whether the expander is disabled
            disable_chevron_rotation (Optional[bool]): Whether to disable chevron rotation animation
            icon (Optional[RouteLitElement]): Icon element shown before the title
            radius (Optional[Union[str, int]]): Border radius
            transition_duration (Optional[int]): Duration of expand/collapse animation in ms
            variant (Optional[Literal["default", "filled", "separated", "contained", "unstyled"]]): Visual variant
            kwargs (Any): Additional props to pass to the accordion component

        Returns:
            RLBuilder: Builder for the expander content
        """
        value = self._new_widget_id("accordionitem", title) if key is None else key
        accordion = self.accordion(
            key=key,
            chevron=chevron,
            chevron_icon_size=chevron_icon_size,
            chevron_position=chevron_position,
            chevron_size=chevron_size,
            disable_chevron_rotation=disable_chevron_rotation,
            radius=radius,
            transition_duration=transition_duration,
            variant=variant,
            value=value if is_open else None,
            **kwargs,
        )
        with accordion:
            item = self.accordion_item(
                label=title,
                key=value,
                disabled=disabled,
                icon=icon,
            )
            return item

    def _format_datetime(self, value: Any) -> Optional[datetime.datetime]:
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return None

    def date_time_picker(
        self,
        label: str,
        value: Optional[Union[datetime.datetime, str]] = None,
        *,
        clearable: Optional[bool] = None,
        columns_to_scroll: Optional[int] = None,
        description: Optional[str] = None,
        disabled: Optional[bool] = None,
        dropdown_type: Optional[Literal["modal", "popover"]] = None,
        error: Optional[str] = None,
        first_day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None,
        header_controls_order: Optional[list[Literal["level", "next", "previous"]]] = None,
        hide_outside_dates: Optional[bool] = None,
        hide_weekdays: Optional[bool] = None,
        highlight_today: Optional[bool] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        label_props: Optional[dict[str, Any]] = None,
        label_separator: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[str] = None,
        level: Optional[Literal["month", "year", "decade"]] = None,
        locale: Optional[str] = None,
        max_date: Optional[Union[datetime.datetime, str]] = None,
        max_level: Optional[Literal["month", "year", "decade"]] = None,
        min_date: Optional[Union[datetime.datetime, str]] = None,
        months_list_format: Optional[str] = None,
        number_of_columns: Optional[int] = None,
        next_label: Optional[str] = None,
        next_icon: Optional[RouteLitElement] = None,
        on_change: Optional[Callable[[datetime.datetime], None]] = None,
        popover_props: Optional[dict[str, Any]] = None,
        presets: Optional[list[dict[str, Any]]] = None,
        previous_icon: Optional[RouteLitElement] = None,
        previous_label: Optional[str] = None,
        placeholder: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_pointer_events: Optional[str] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        sort_dates: Optional[bool] = None,
        submit_button_props: Optional[dict[str, Any]] = None,
        time_picker_props: Optional[dict[str, Any]] = None,
        value_format: Optional[str] = None,
        weekday_format: Optional[str] = None,
        weekend_days: Optional[list[Literal[0, 1, 2, 3, 4, 5, 6]]] = None,
        with_asterisk: Optional[bool] = None,
        with_cell_spacing: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_seconds: Optional[bool] = None,
        with_week_numbers: Optional[bool] = None,
        wrapper_props: Optional[dict[str, Any]] = None,
        year_label_format: Optional[str] = None,
        years_list_format: Optional[str] = None,
        pointer: Optional[bool] = None,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[datetime.datetime]:
        """
        Date-time picker input with calendar and time selection.

        Args:
            label (str): Field label.
            value (Optional[Union[datetime.datetime, str]]): Current value.
            clearable (Optional[bool]): Show clear button.
            columns_to_scroll (Optional[int]): Number of months to scroll.
            description (Optional[str]): Helper text under the label.
            disabled (Optional[bool]): Disable interaction.
            dropdown_type (Optional[Literal["modal", "popover"]]): Dropdown type.
            error (Optional[str]): Error message.
            first_day_of_week (Optional[Literal[0,1,2,3,4,5,6]]): First day of week.
            header_controls_order (Optional[list[Literal["level", "next", "previous"]]]): Header controls order.
            hide_outside_dates (Optional[bool]): Hide outside month dates.
            hide_weekdays (Optional[bool]): Hide weekday labels.
            highlight_today (Optional[bool]): Highlight current date.
            input_size (Optional[str]): Control size.
            input_wrapper_order (Optional[list[str]]): Input wrapper parts order.
            label_props (Optional[dict[str, Any]]): Label props.
            label_separator (Optional[str]): Separator between date and time.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_props (Optional[dict[str, Any]]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            level (Optional[Literal["month", "year", "decade"]]): Initial calendar level.
            locale (Optional[str]): Locale code.
            max_date (Optional[Union[datetime.datetime, str]]): Max date.
            max_level (Optional[Literal["month", "year", "decade"]]): Max calendar level.
            min_date (Optional[Union[datetime.datetime, str]]): Min date.
            months_list_format (Optional[str]): Months list format.
            number_of_columns (Optional[int]): Number of months displayed.
            next_label (Optional[str]): Next button label.
            next_icon (Optional[RouteLitElement]): Next button icon.
            on_change (Optional[Callable[[datetime.datetime], None]]): Change handler.
            popover_props (Optional[dict[str, Any]]): Popover props.
            presets (Optional[list[dict[str, Any]]]): Presets configuration.
            previous_icon (Optional[RouteLitElement]): Previous button icon.
            previous_label (Optional[str]): Previous button label.
            placeholder (Optional[str]): Input placeholder.
            radius (Optional[Union[str, int]]): Corner radius.
            read_only (Optional[bool]): Read-only state.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_pointer_events (Optional[str]): Pointer events for right section.
            right_section_props (Optional[dict[str, Any]]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            sort_dates (Optional[bool]): Sort selected dates.
            submit_button_props (Optional[dict[str, Any]]): Submit button props.
            time_picker_props (Optional[dict[str, Any]]): Time picker props.
            value_format (Optional[str]): Output value format.
            weekday_format (Optional[str]): Weekday label format.
            weekend_days (Optional[list[Literal[0,1,2,3,4,5,6]]]): Weekend days indices.
            with_asterisk (Optional[bool]): Show required asterisk.
            with_cell_spacing (Optional[bool]): Add spacing between cells.
            with_error_styles (Optional[bool]): Apply error styles.
            with_seconds (Optional[bool]): Include seconds selector.
            with_week_numbers (Optional[bool]): Show week numbers.
            wrapper_props (Optional[dict[str, Any]]): Wrapper props.
            year_label_format (Optional[str]): Year label format.
            years_list_format (Optional[str]): Years list format.
            pointer (Optional[bool]): Use pointer cursor.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            Optional[datetime.datetime]: Current value.
        """
        return cast(
            Optional[datetime.datetime],
            self._x_input(
                "datetimepicker",
                key or self._new_widget_id("datetimepicker", label),
                clearable=clearable,
                columnsToScroll=columns_to_scroll,
                description=description,
                disabled=disabled,
                dropdownType=dropdown_type,
                error=error,
                firstDayOfWeek=first_day_of_week,
                headerControlsOrder=header_controls_order,
                hideOutsideDates=hide_outside_dates,
                hideWeekdays=hide_weekdays,
                highlightToday=highlight_today,
                inputSize=input_size,
                inputWrapperOrder=input_wrapper_order,
                label=label,
                labelProps=label_props,
                labelSeparator=label_separator,
                value=value,
                leftSection=left_section,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                level=level,
                locale=locale,
                maxDate=max_date,
                maxLevel=max_level,
                minDate=min_date,
                monthsListFormat=months_list_format,
                nextIcon=next_icon,
                nextLabel=next_label,
                numberOfColumns=number_of_columns,
                on_change=on_change,
                popoverProps=popover_props,
                presets=presets,
                previousIcon=previous_icon,
                previousLabel=previous_label,
                placeholder=placeholder,
                radius=radius,
                readOnly=read_only,
                required=required,
                rightSection=right_section,
                rightSectionPointerEvents=right_section_pointer_events,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                rl_format_func=self._format_datetime,
                size=size,
                sortDates=sort_dates,
                submitButtonProps=submit_button_props,
                timePickerProps=time_picker_props,
                valueFormat=value_format,
                weekdayFormat=weekday_format,
                weekendDays=weekend_days,
                withAsterisk=with_asterisk,
                withCellSpacing=with_cell_spacing,
                withErrorStyles=with_error_styles,
                withSeconds=with_seconds,
                withWeekNumbers=with_week_numbers,
                wrapperProps=wrapper_props,
                yearLabelFormat=year_label_format,
                yearsListFormat=years_list_format,
                pointer=pointer,
                **kwargs,
            ),
        )

    def _format_date_picker(
        self, value: Any
    ) -> Optional[Union[datetime.date, list[datetime.date], tuple[datetime.date, datetime.date]]]:
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            return datetime.date.fromisoformat(value)
        if isinstance(value, list):
            return [datetime.date.fromisoformat(x) if isinstance(x, str) else x for x in value]
        return None

    def date_picker(
        self,
        label: str,
        value: Optional[
            Union[
                datetime.date,
                str,
                list[str],
                list[datetime.date],
                tuple[str, str],
                tuple[datetime.date, datetime.date],
            ]
        ] = None,
        *,
        allow_deselect: Optional[bool] = None,
        allow_single_date_in_range: Optional[bool] = None,
        aria_labels: Optional[dict] = None,
        columns_to_scroll: Optional[int] = None,
        decade_label_format: Optional[str] = None,
        default_level: Optional[Literal["month", "year", "decade"]] = None,
        description: Optional[str] = None,
        enable_keyboard_navigation: Optional[bool] = None,
        first_day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None,
        header_controls_order: Optional[list[Literal["level", "next", "previous"]]] = None,
        hide_outside_dates: Optional[bool] = None,
        hide_weekdays: Optional[bool] = None,
        highlight_today: Optional[bool] = None,
        key: Optional[str] = None,
        level: Optional[str] = None,
        locale: Optional[str] = None,
        max_date: Optional[Union[str, datetime.date]] = None,
        max_level: Optional[str] = None,
        min_date: Optional[Union[str, datetime.date]] = None,
        month_label_format: Optional[str] = None,
        months_list_format: Optional[str] = None,
        next_icon: Optional[RouteLitElement] = None,
        next_label: Optional[str] = None,
        number_of_columns: Optional[int] = None,
        on_change: Optional[
            Callable[
                [
                    Union[
                        datetime.date,
                        list[datetime.date],
                        tuple[datetime.date, datetime.date],
                    ]
                ],
                None,
            ]
        ] = None,
        presets: Optional[list] = None,
        previous_icon: Optional[RouteLitElement] = None,
        previous_label: Optional[str] = None,
        size: Optional[str] = None,
        type: Optional[Literal["default", "range", "multiple"]] = None,  # noqa: A002
        weekday_format: Optional[str] = None,
        weekend_days: Optional[list[Literal[0, 1, 2, 3, 4, 5, 6]]] = None,
        with_cell_spacing: Optional[bool] = None,
        with_week_numbers: Optional[bool] = None,
        year_label_format: Optional[str] = None,
        years_list_format: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Union[datetime.date, list[datetime.date], tuple[datetime.date, datetime.date]]]:
        """
        Calendar date picker supporting single, range, and multiple modes.

        Args:
            label (str): Field label.
            value (Optional[...]): Current value in the selected mode.
            allow_deselect (Optional[bool]): Allow clearing selection.
            allow_single_date_in_range (Optional[bool]): Allow single date in range mode.
            aria_labels (Optional[dict]): ARIA labels.
            columns_to_scroll (Optional[int]): Months to scroll.
            decade_label_format (Optional[str]): Decade label format.
            default_level (Optional[Literal["month", "year", "decade"]]): Initial calendar level.
            description (Optional[str]): Helper text under the label.
            enable_keyboard_navigation (Optional[bool]): Enable keyboard navigation.
            first_day_of_week (Optional[Literal[0,1,2,3,4,5,6]]): First day of week.
            header_controls_order (Optional[list[...]]): Header controls order.
            hide_outside_dates (Optional[bool]): Hide outside month dates.
            hide_weekdays (Optional[bool]): Hide weekday labels.
            highlight_today (Optional[bool]): Highlight current date.
            key (Optional[str]): Explicit element key.
            level (Optional[str]): Current level.
            locale (Optional[str]): Locale code.
            max_date (Optional[Union[str, datetime.date]]): Max date.
            max_level (Optional[str]): Max level.
            min_date (Optional[Union[str, datetime.date]]): Min date.
            month_label_format (Optional[str]): Month label format.
            months_list_format (Optional[str]): Months list format.
            next_icon (Optional[RouteLitElement]): Next button icon.
            next_label (Optional[str]): Next button label.
            number_of_columns (Optional[int]): Months displayed.
            on_change (Optional[Callable[[...], None]]): Change handler.
            presets (Optional[list]): Preset ranges.
            previous_icon (Optional[RouteLitElement]): Previous button icon.
            previous_label (Optional[str]): Previous button label.
            size (Optional[str]): Control size.
            type (Optional[Literal["default", "range", "multiple"]]): Picker mode.
            weekday_format (Optional[str]): Weekday label format.
            weekend_days (Optional[list[...]]): Weekend days indices.
            with_cell_spacing (Optional[bool]): Add spacing between cells.
            with_week_numbers (Optional[bool]): Show week numbers.
            year_label_format (Optional[str]): Year label format.
            years_list_format (Optional[str]): Years list format.
            kwargs: Additional props to set.

        Returns:
            Optional[Union[datetime.date, list[datetime.date], tuple[datetime.date, datetime.date]]]: Current value.
        """
        return cast(
            Optional[
                Union[
                    datetime.date,
                    list[datetime.date],
                    tuple[datetime.date, datetime.date],
                ]
            ],
            self._x_input(
                "datepicker",
                key or self._new_widget_id("datepicker", label),
                label=label,
                description=description,
                value=value,
                allowDeselect=allow_deselect,
                allowSingleDateInRange=allow_single_date_in_range,
                ariaLabels=aria_labels,
                columnsToScroll=columns_to_scroll,
                decadeLabelFormat=decade_label_format,
                defaultLevel=default_level,
                enableKeyboardNavigation=enable_keyboard_navigation,
                firstDayOfWeek=first_day_of_week,
                headerControlsOrder=header_controls_order,
                hideOutsideDates=hide_outside_dates,
                hideWeekdays=hide_weekdays,
                highlightToday=highlight_today,
                level=level,
                locale=locale,
                maxDate=max_date,
                maxLevel=max_level,
                minDate=min_date,
                monthLabelFormat=month_label_format,
                monthsListFormat=months_list_format,
                nextIcon=next_icon,
                nextLabel=next_label,
                numberOfColumns=number_of_columns,
                onChange=on_change,
                presets=presets,
                previousIcon=previous_icon,
                previousLabel=previous_label,
                size=size,
                type=type,
                weekdayFormat=weekday_format,
                weekendDays=weekend_days,
                withCellSpacing=with_cell_spacing,
                withWeekNumbers=with_week_numbers,
                yearLabelFormat=year_label_format,
                yearsListFormat=years_list_format,
                rl_format_func=self._format_date_picker,
                **kwargs,
            ),
        )

    def date_picker_input(
        self,
        label: str,
        value: Optional[
            Union[
                datetime.date,
                str,
                list[str],
                list[datetime.date],
                tuple[str, str],
                tuple[datetime.date, datetime.date],
            ]
        ] = None,
        *,
        key: Optional[str] = None,
        description: Optional[str] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        allow_deselect: Optional[bool] = None,
        allow_single_date_in_range: Optional[bool] = None,
        aria_labels: Optional[dict] = None,
        clear_button_props: Optional[dict] = None,
        clearable: Optional[bool] = None,
        close_on_change: Optional[bool] = None,
        columns_to_scroll: Optional[int] = None,
        decade_label_format: Optional[str] = None,
        default_level: Optional[Literal["month", "year", "decade"]] = None,
        description_props: Optional[dict] = None,
        disabled: Optional[bool] = None,
        dropdown_type: Optional[Literal["modal", "popover"]] = None,
        enable_keyboard_navigation: Optional[bool] = None,
        error: Optional[str] = None,
        error_props: Optional[dict] = None,
        first_day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None,
        header_controls_order: Optional[list[Literal["level", "next", "previous"]]] = None,
        hide_outside_dates: Optional[bool] = None,
        hide_weekdays: Optional[bool] = None,
        highlight_today: Optional[bool] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[Literal["input", "label", "description", "error"]]] = None,
        label_props: Optional[dict] = None,
        label_separator: Optional[str] = None,
        left_section: Optional[RouteLitElement] = None,
        left_section_pointer_events: Optional[str] = None,
        left_section_props: Optional[dict] = None,
        left_section_width: Optional[str] = None,
        level: Optional[Literal["month", "year", "decade"]] = None,
        locale: Optional[str] = None,
        max_date: Optional[Union[str, datetime.date]] = None,
        max_level: Optional[Literal["month", "year", "decade"]] = None,
        min_date: Optional[Union[str, datetime.date]] = None,
        modal_props: Optional[dict] = None,
        month_label_format: Optional[str] = None,
        months_list_format: Optional[str] = None,
        next_icon: Optional[RouteLitElement] = None,
        next_label: Optional[str] = None,
        number_of_columns: Optional[int] = None,
        placeholder: Optional[str] = None,
        pointer: Optional[bool] = None,
        popover_props: Optional[dict] = None,
        presets: Optional[list] = None,
        previous_icon: Optional[RouteLitElement] = None,
        previous_label: Optional[str] = None,
        radius: Optional[Union[str, int]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        right_section: Optional[RouteLitElement] = None,
        right_section_pointer_events: Optional[str] = None,
        right_section_props: Optional[dict] = None,
        right_section_width: Optional[str] = None,
        size: Optional[str] = None,
        sort_dates: Optional[bool] = None,
        type: Optional[str] = None,  # noqa: A002
        value_format: Optional[str] = None,
        weekday_format: Optional[str] = None,
        weekend_days: Optional[list] = None,
        with_asterisk: Optional[bool] = None,
        with_cell_spacing: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_week_numbers: Optional[bool] = None,
        wrapper_props: Optional[dict] = None,
        year_label_format: Optional[str] = None,
        years_list_format: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Union[datetime.date, list[datetime.date], tuple[datetime.date, datetime.date]]]:
        """
        Text input with integrated date picker dropdown.

        Args:
            label (str): Field label.
            value (Optional[...]): Current value in the selected mode.
            key (Optional[str]): Explicit element key.
            description (Optional[str]): Helper text.
            on_change (Optional[Callable[[Any], None]]): Change handler.
            allow_deselect (Optional[bool]): Allow clearing selection.
            allow_single_date_in_range (Optional[bool]): Allow single date in range mode.
            aria_labels (Optional[dict]): ARIA labels.
            clear_button_props (Optional[dict]): Clear button props.
            clearable (Optional[bool]): Enable clear button.
            close_on_change (Optional[bool]): Close dropdown on change.
            columns_to_scroll (Optional[int]): Months to scroll.
            decade_label_format (Optional[str]): Decade label format.
            default_level (Optional[Literal["month", "year", "decade"]]): Initial calendar level.
            description_props (Optional[dict]): Description props.
            disabled (Optional[bool]): Disable interaction.
            dropdown_type (Optional[Literal["modal", "popover"]]): Dropdown type.
            enable_keyboard_navigation (Optional[bool]): Enable keyboard navigation.
            error (Optional[str]): Error message.
            error_props (Optional[dict]): Error props.
            first_day_of_week (Optional[Literal[0,1,2,3,4,5,6]]): First day of week.
            header_controls_order (Optional[list[...]]): Header controls order.
            hide_outside_dates (Optional[bool]): Hide outside month dates.
            hide_weekdays (Optional[bool]): Hide weekday labels.
            highlight_today (Optional[bool]): Highlight current date.
            input_size (Optional[str]): Control size.
            input_wrapper_order (Optional[list[Literal["input","label","description","error"]]]): Wrapper parts order.
            label_props (Optional[dict]): Label props.
            label_separator (Optional[str]): Separator for range values.
            left_section (Optional[RouteLitElement]): Left adornment.
            left_section_pointer_events (Optional[str]): Pointer events for left section.
            left_section_props (Optional[dict]): Left adornment props.
            left_section_width (Optional[str]): Left adornment width.
            level (Optional[Literal["month", "year", "decade"]]): Initial calendar level.
            locale (Optional[str]): Locale code.
            max_date (Optional[Union[str, datetime.date]]): Max date.
            max_level (Optional[Literal["month", "year", "decade"]]): Max calendar level.
            min_date (Optional[Union[str, datetime.date]]): Min date.
            modal_props (Optional[dict]): Modal props.
            month_label_format (Optional[str]): Month label format.
            months_list_format (Optional[str]): Months list format.
            next_icon (Optional[RouteLitElement]): Next button icon.
            next_label (Optional[str]): Next button label.
            number_of_columns (Optional[int]): Months displayed.
            placeholder (Optional[str]): Input placeholder.
            pointer (Optional[bool]): Use pointer cursor.
            popover_props (Optional[dict]): Popover props.
            presets (Optional[list]): Preset ranges.
            previous_icon (Optional[RouteLitElement]): Previous button icon.
            previous_label (Optional[str]): Previous button label.
            radius (Optional[Union[str, int]]): Corner radius.
            read_only (Optional[bool]): Read-only state.
            required (Optional[bool]): Mark as required.
            right_section (Optional[RouteLitElement]): Right adornment.
            right_section_pointer_events (Optional[str]): Pointer events for right section.
            right_section_props (Optional[dict]): Right adornment props.
            right_section_width (Optional[str]): Right adornment width.
            size (Optional[str]): Control size.
            sort_dates (Optional[bool]): Sort selected dates.
            type (Optional[str]): Picker mode.
            value_format (Optional[str]): Output value format.
            weekday_format (Optional[str]): Weekday label format.
            weekend_days (Optional[list]): Weekend days indices.
            with_asterisk (Optional[bool]): Show required asterisk.
            with_cell_spacing (Optional[bool]): Add spacing between cells.
            with_error_styles (Optional[bool]): Apply error styles.
            with_week_numbers (Optional[bool]): Show week numbers.
            wrapper_props (Optional[dict]): Wrapper props.
            year_label_format (Optional[str]): Year label format.
            years_list_format (Optional[str]): Years list format.
            kwargs: Additional props to set.

        Returns:
            Optional[Union[datetime.date, list[datetime.date], tuple[datetime.date, datetime.date]]]: Current value.
        """
        return cast(
            Optional[
                Union[
                    datetime.date,
                    list[datetime.date],
                    tuple[datetime.date, datetime.date],
                ]
            ],
            self._x_input(
                "datepickerinput",
                key or self._new_widget_id("datepickerinput", label),
                label=label,
                description=description,
                value=value,
                allowDeselect=allow_deselect,
                allowSingleDateInRange=allow_single_date_in_range,
                ariaLabels=aria_labels,
                clearButtonProps=clear_button_props,
                clearable=clearable,
                closeOnChange=close_on_change,
                columnsToScroll=columns_to_scroll,
                decadeLabelFormat=decade_label_format,
                defaultLevel=default_level,
                descriptionProps=description_props,
                disabled=disabled,
                dropdownType=dropdown_type,
                enableKeyboardNavigation=enable_keyboard_navigation,
                error=error,
                errorProps=error_props,
                firstDayOfWeek=first_day_of_week,
                headerControlsOrder=header_controls_order,
                hideOutsideDates=hide_outside_dates,
                hideWeekdays=hide_weekdays,
                highlightToday=highlight_today,
                inputSize=input_size,
                inputWrapperOrder=input_wrapper_order,
                labelProps=label_props,
                labelSeparator=label_separator,
                leftSection=left_section,
                leftSectionPointerEvents=left_section_pointer_events,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                level=level,
                locale=locale,
                maxDate=max_date,
                maxLevel=max_level,
                minDate=min_date,
                modalProps=modal_props,
                monthLabelFormat=month_label_format,
                monthsListFormat=months_list_format,
                nextIcon=next_icon,
                nextLabel=next_label,
                numberOfColumns=number_of_columns,
                on_change=on_change,
                placeholder=placeholder,
                pointer=pointer,
                popoverProps=popover_props,
                presets=presets,
                previousIcon=previous_icon,
                previousLabel=previous_label,
                radius=radius,
                readOnly=read_only,
                required=required,
                rightSection=right_section,
                rightSectionPointerEvents=right_section_pointer_events,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                size=size,
                sortDates=sort_dates,
                type=type,
                valueFormat=value_format,
                weekdayFormat=weekday_format,
                weekendDays=weekend_days,
                withAsterisk=with_asterisk,
                withCellSpacing=with_cell_spacing,
                withErrorStyles=with_error_styles,
                withWeekNumbers=with_week_numbers,
                wrapperProps=wrapper_props,
                yearLabelFormat=year_label_format,
                yearsListFormat=years_list_format,
                rl_format_func=self._format_date_picker,
                **kwargs,
            ),
        )

    def _format_time(self, value: Optional[Union[datetime.time, str]]) -> Optional[datetime.time]:
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.time.fromisoformat(value)
        return value

    def time_input(
        self,
        label: str,
        value: Optional[Union[datetime.time, str]] = None,
        *,
        key: Optional[str] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        description: Optional[Any] = None,
        description_props: Optional[dict[str, Any]] = None,
        disabled: Optional[bool] = None,
        error: Optional[Any] = None,
        error_props: Optional[dict[str, Any]] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        label_props: Optional[dict[str, Any]] = None,
        left_section: Optional[Any] = None,
        left_section_pointer_events: Optional[str] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[Union[str, int]] = None,
        max_time: Optional[str] = None,
        min_time: Optional[str] = None,
        pointer: Optional[bool] = None,
        radius: Optional[Union[str, int]] = None,
        required: Optional[bool] = None,
        right_section: Optional[Any] = None,
        right_section_pointer_events: Optional[str] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[Union[str, int]] = None,
        size: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_seconds: Optional[bool] = None,
        wrapper_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[datetime.time]:
        """
        Time input with support for parsing from string.

        Args:
            label (str): Field label.
            value (Optional[Union[datetime.time, str]]): Current value.
            key (Optional[str]): Explicit element key.
            on_change (Optional[Callable[[Any], None]]): Change handler.
            description (Optional[Any]): Contents of Input.Description component.
            description_props (Optional[dict[str, Any]]): Props passed to Input.Description component.
            disabled (Optional[bool]): Sets disabled attribute on input element.
            error (Optional[Any]): Contents of Input.Error component.
            error_props (Optional[dict[str, Any]]): Props passed to Input.Error component.
            input_size (Optional[str]): Size attribute for input element.
            input_wrapper_order (Optional[list[str]]): Controls order of elements.
            label_props (Optional[dict[str, Any]]): Props passed to Input.Label component.
            left_section (Optional[Any]): Content displayed on left side of input.
            left_section_pointer_events (Optional[str]): Pointer events style for left section.
            left_section_props (Optional[dict[str, Any]]): Props for left section element.
            left_section_width (Optional[Union[str, int]]): Width of left section.
            max_time (Optional[str]): Maximum possible time value.
            min_time (Optional[str]): Minimum possible time value.
            pointer (Optional[bool]): Whether input should have pointer cursor.
            radius (Optional[Union[str, int]]): Border radius value.
            required (Optional[bool]): Whether input is required.
            right_section (Optional[Any]): Content displayed on right side of input.
            right_section_pointer_events (Optional[str]): Pointer events style for right section.
            right_section_props (Optional[dict[str, Any]]): Props for right section element.
            right_section_width (Optional[Union[str, int]]): Width of right section.
            size (Optional[str]): Controls input height and padding.
            with_asterisk (Optional[bool]): Whether to show required asterisk.
            with_error_styles (Optional[bool]): Whether to show error styling.
            with_seconds (Optional[bool]): Whether to show seconds input.
            wrapper_props (Optional[dict[str, Any]]): Props for root element.
            kwargs: Additional props to set.

        Returns:
            Optional[datetime.time]: Current value.
        """
        return cast(
            Optional[datetime.time],
            self._x_input(
                "timeinput",
                key=key or self._new_widget_id("timeinput", label),
                label=label,
                value=value,
                description=description,
                descriptionProps=description_props,
                disabled=disabled,
                error=error,
                errorProps=error_props,
                inputSize=input_size,
                inputWrapperOrder=input_wrapper_order,
                labelProps=label_props,
                leftSection=left_section,
                leftSectionPointerEvents=left_section_pointer_events,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                maxTime=max_time,
                minTime=min_time,
                pointer=pointer,
                radius=radius,
                required=required,
                rightSection=right_section,
                rightSectionPointerEvents=right_section_pointer_events,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                size=size,
                withAsterisk=with_asterisk,
                withErrorStyles=with_error_styles,
                withSeconds=with_seconds,
                wrapperProps=wrapper_props,
                rl_format_func=self._format_time,
                on_change=on_change,
                **kwargs,
            ),
        )

    def time_picker(
        self,
        label: str,
        value: Optional[Union[datetime.time, str]] = None,
        *,
        key: Optional[str] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        am_pm_input_label: Optional[str] = None,
        am_pm_labels: Optional[dict[str, str]] = None,
        am_pm_select_props: Optional[dict[str, Any]] = None,
        clear_button_props: Optional[dict[str, Any]] = None,
        clearable: Optional[bool] = None,
        description: Optional[Any] = None,
        description_props: Optional[dict[str, Any]] = None,
        disabled: Optional[bool] = None,
        error: Optional[Any] = None,
        error_props: Optional[dict[str, Any]] = None,
        form: Optional[str] = None,
        format: Optional[str] = None,  # noqa: A002
        hidden_input_props: Optional[dict[str, Any]] = None,
        hours_input_label: Optional[str] = None,
        hours_input_props: Optional[dict[str, Any]] = None,
        hours_step: Optional[int] = None,
        input_size: Optional[str] = None,
        input_wrapper_order: Optional[list[str]] = None,
        label_props: Optional[dict[str, Any]] = None,
        left_section: Optional[Any] = None,
        left_section_pointer_events: Optional[str] = None,
        left_section_props: Optional[dict[str, Any]] = None,
        left_section_width: Optional[Union[str, int]] = None,
        max: Optional[str] = None,  # noqa: A002
        max_dropdown_content_height: Optional[int] = None,
        min: Optional[str] = None,  # noqa: A002
        minutes_input_label: Optional[str] = None,
        minutes_input_props: Optional[dict[str, Any]] = None,
        minutes_step: Optional[int] = None,
        name: Optional[str] = None,
        pointer: Optional[bool] = None,
        popover_props: Optional[dict[str, Any]] = None,
        presets: Optional[Any] = None,
        radius: Optional[Union[str, int]] = None,
        read_only: Optional[bool] = None,
        required: Optional[bool] = None,
        right_section: Optional[Any] = None,
        right_section_pointer_events: Optional[str] = None,
        right_section_props: Optional[dict[str, Any]] = None,
        right_section_width: Optional[Union[str, int]] = None,
        scroll_area_props: Optional[dict[str, Any]] = None,
        seconds_input_label: Optional[str] = None,
        seconds_input_props: Optional[dict[str, Any]] = None,
        seconds_step: Optional[int] = None,
        size: Optional[str] = None,
        with_asterisk: Optional[bool] = None,
        with_dropdown: Optional[bool] = None,
        with_error_styles: Optional[bool] = None,
        with_seconds: Optional[bool] = None,
        wrapper_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[datetime.time]:
        """
        Time picker with support for parsing from string.

        Args:
            label (str): Label text.
            value (Optional[Union[datetime.time, str]]): Current value.
            key (Optional[str]): Unique key for the widget.
            on_change (Optional[Callable[[Any], None]]): Called when value changes.
            am_pm_input_label (Optional[str]): aria-label of am/pm input.
            am_pm_labels (Optional[dict[str, str]]): Labels used for am/pm values.
            am_pm_select_props (Optional[dict[str, Any]]): Props for am/pm select.
            clear_button_props (Optional[dict[str, Any]]): Props for clear button.
            clearable (Optional[bool]): Whether clear button should be displayed.
            description (Optional[Any]): Description content.
            description_props (Optional[dict[str, Any]]): Props for description.
            disabled (Optional[bool]): Whether component is disabled.
            error (Optional[Any]): Error content.
            error_props (Optional[dict[str, Any]]): Props for error.
            form (Optional[str]): Form prop for hidden input.
            format (Optional[str]): Time format ('12h' or '24h').
            hidden_input_props (Optional[dict[str, Any]]): Props for hidden input.
            hours_input_label (Optional[str]): aria-label of hours input.
            hours_input_props (Optional[dict[str, Any]]): Props for hours input.
            hours_step (Optional[int]): Hours increment/decrement step.
            input_size (Optional[str]): Size attribute for input element.
            input_wrapper_order (Optional[list[str]]): Order of elements.
            label_props (Optional[dict[str, Any]]): Props for label.
            left_section (Optional[Any]): Left section content.
            left_section_pointer_events (Optional[str]): Left section pointer events.
            left_section_props (Optional[dict[str, Any]]): Props for left section.
            left_section_width (Optional[Union[str, int]]): Left section width.
            max (Optional[str]): Max time value (hh:mm:ss).
            max_dropdown_content_height (Optional[int]): Max dropdown height in px.
            min (Optional[str]): Min time value (hh:mm:ss).
            minutes_input_label (Optional[str]): aria-label of minutes input.
            minutes_input_props (Optional[dict[str, Any]]): Props for minutes input.
            minutes_step (Optional[int]): Minutes increment/decrement step.
            name (Optional[str]): Name prop for hidden input.
            pointer (Optional[bool]): Whether to show pointer cursor.
            popover_props (Optional[dict[str, Any]]): Props for popover.
            presets (Optional[Any]): Time presets for dropdown.
            radius (Optional[Union[str, int]]): Border radius.
            read_only (Optional[bool]): Whether value is read-only.
            required (Optional[bool]): Whether field is required.
            right_section (Optional[Any]): Right section content.
            right_section_pointer_events (Optional[str]): Right section pointer events.
            right_section_props (Optional[dict[str, Any]]): Props for right section.
            right_section_width (Optional[Union[str, int]]): Right section width.
            scroll_area_props (Optional[dict[str, Any]]): Props for scroll areas.
            seconds_input_label (Optional[str]): aria-label of seconds input.
            seconds_input_props (Optional[dict[str, Any]]): Props for seconds input.
            seconds_step (Optional[int]): Seconds increment/decrement step.
            size (Optional[str]): Controls input height and padding.
            value (Optional[Union[datetime.time, str]]): Current value.
            with_asterisk (Optional[bool]): Whether to show required asterisk.
            with_dropdown (Optional[bool]): Whether to show dropdown.
            with_error_styles (Optional[bool]): Whether to show error styling.
            with_seconds (Optional[bool]): Whether to show seconds input.
            wrapper_props (Optional[dict[str, Any]]): Props for root element.
            kwargs: Additional props to set.

        Returns:
            Optional[datetime.time]: Current value.
        """
        return cast(
            Optional[datetime.time],
            self._x_input(
                "timepicker",
                key=key or self._new_widget_id("timepicker", label),
                label=label,
                value=value,
                amPmInputLabel=am_pm_input_label,
                amPmLabels=am_pm_labels,
                amPmSelectProps=am_pm_select_props,
                clearButtonProps=clear_button_props,
                clearable=clearable,
                description=description,
                descriptionProps=description_props,
                disabled=disabled,
                error=error,
                errorProps=error_props,
                form=form,
                format=format,
                hiddenInputProps=hidden_input_props,
                hoursInputLabel=hours_input_label,
                hoursInputProps=hours_input_props,
                hoursStep=hours_step,
                inputSize=input_size,
                inputWrapperOrder=input_wrapper_order,
                labelProps=label_props,
                leftSection=left_section,
                leftSectionPointerEvents=left_section_pointer_events,
                leftSectionProps=left_section_props,
                leftSectionWidth=left_section_width,
                max=max,
                maxDropdownContentHeight=max_dropdown_content_height,
                min=min,
                minutesInputLabel=minutes_input_label,
                minutesInputProps=minutes_input_props,
                minutesStep=minutes_step,
                name=name,
                pointer=pointer,
                popoverProps=popover_props,
                presets=presets,
                radius=radius,
                readOnly=read_only,
                required=required,
                rightSection=right_section,
                rightSectionPointerEvents=right_section_pointer_events,
                rightSectionProps=right_section_props,
                rightSectionWidth=right_section_width,
                scrollAreaProps=scroll_area_props,
                secondsInputLabel=seconds_input_label,
                secondsInputProps=seconds_input_props,
                secondsStep=seconds_step,
                size=size,
                withAsterisk=with_asterisk,
                withDropdown=with_dropdown,
                withErrorStyles=with_error_styles,
                withSeconds=with_seconds,
                wrapperProps=wrapper_props,
                rl_format_func=self._format_time,
                on_change=on_change,
                **kwargs,
            ),
        )

    def area_chart(
        self,
        data: list,
        data_key: str,
        series: list[dict[str, Any]],
        *,
        key: Optional[str] = None,
        active_dot_props: Optional[dict[str, Any]] = None,
        area_chart_props: Optional[dict[str, Any]] = None,
        area_props: Optional[dict[str, Any]] = None,
        connect_nulls: Optional[bool] = None,
        curve_type: Optional[str] = None,
        dot_props: Optional[dict[str, Any]] = None,
        fill_opacity: float = 0.2,
        grid_axis: Optional[str] = None,
        grid_color: Optional[str] = None,
        grid_props: Optional[dict[str, Any]] = None,
        legend_props: Optional[dict[str, Any]] = None,
        orientation: Optional[str] = None,
        reference_lines: Optional[list[dict[str, Any]]] = None,
        right_y_axis_label: Optional[str] = None,
        right_y_axis_props: Optional[dict[str, Any]] = None,
        split_colors: Optional[list[str]] = None,
        split_offset: Optional[float] = None,
        stroke_dasharray: Optional[Union[str, int]] = None,
        stroke_width: Optional[int] = None,
        text_color: Optional[str] = None,
        tick_line: Optional[str] = None,
        tooltip_animation_duration: int = 0,
        tooltip_props: Optional[dict[str, Any]] = None,
        type: Optional[str] = None,  # noqa: A002
        unit: Optional[str] = None,
        with_dots: Optional[bool] = None,
        with_gradient: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_point_labels: Optional[bool] = None,
        with_right_y_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_x_axis: Optional[bool] = None,
        with_y_axis: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_label: Optional[str] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Area chart for time series or continuous data.

        Args:
            data (list): Dataset.
            data_key (str): X-axis data key.
            series (list[dict[str, Any]]): Series configuration.
            key (Optional[str]): Explicit element key.
            active_dot_props (Optional[dict[str, Any]]): Active dot props.
            area_chart_props (Optional[dict[str, Any]]): Chart container props.
            area_props (Optional[dict[str, Any]]): Area props.
            connect_nulls (Optional[bool]): Connect across null values.
            curve_type (Optional[str]): Curve interpolation type.
            dot_props (Optional[dict[str, Any]]): Dot props.
            fill_opacity (float): Fill opacity for area.
            grid_axis (Optional[str]): Grid axis.
            grid_color (Optional[str]): Grid color.
            grid_props (Optional[dict[str, Any]]): Grid props.
            legend_props (Optional[dict[str, Any]]): Legend props.
            orientation (Optional[str]): Chart orientation.
            reference_lines (Optional[list[dict[str, Any]]]): Reference lines.
            right_y_axis_label (Optional[str]): Secondary Y axis label.
            right_y_axis_props (Optional[dict[str, Any]]): Secondary Y axis props.
            split_colors (Optional[list[str]]): Split area colors.
            split_offset (Optional[float]): Split offset value.
            stroke_dasharray (Optional[Union[str, int]]): Stroke dash pattern.
            stroke_width (Optional[int]): Line width.
            text_color (Optional[str]): Text color.
            tick_line (Optional[str]): Tick line display.
            tooltip_animation_duration (int): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            type (Optional[str]): Chart type variant.
            unit (Optional[str]): Unit suffix.
            with_dots (Optional[bool]): Show dots.
            with_gradient (Optional[bool]): Fill with gradient.
            with_legend (Optional[bool]): Show legend.
            with_point_labels (Optional[bool]): Show point labels.
            with_right_y_axis (Optional[bool]): Enable right Y axis.
            with_tooltip (Optional[bool]): Show tooltip.
            with_x_axis (Optional[bool]): Show X axis.
            with_y_axis (Optional[bool]): Show Y axis.
            x_axis_label (Optional[str]): X axis label.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_label (Optional[str]): Y axis label.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the area chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="areachart",
            key=key or self._new_text_id("areachart"),
            props={
                "data": data,
                "dataKey": data_key,
                "series": series,
                "activeDotProps": active_dot_props,
                "areaChartProps": area_chart_props,
                "areaProps": area_props,
                "connectNulls": connect_nulls,
                "curveType": curve_type,
                "dotProps": dot_props,
                "fillOpacity": fill_opacity,
                "gridAxis": grid_axis,
                "gridColor": grid_color,
                "gridProps": grid_props,
                "legendProps": legend_props,
                "orientation": orientation,
                "referenceLines": reference_lines,
                "rightYAxisLabel": right_y_axis_label,
                "rightYAxisProps": right_y_axis_props,
                "splitColors": split_colors,
                "splitOffset": split_offset,
                "strokeDasharray": stroke_dasharray,
                "strokeWidth": stroke_width,
                "textColor": text_color,
                "tickLine": tick_line,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "type": type,
                "unit": unit,
                "withDots": with_dots,
                "withGradient": with_gradient,
                "withLegend": with_legend,
                "withPointLabels": with_point_labels,
                "withRightYAxis": with_right_y_axis,
                "withTooltip": with_tooltip,
                "withXAxis": with_x_axis,
                "withYAxis": with_y_axis,
                "xAxisLabel": x_axis_label,
                "xAxisProps": x_axis_props,
                "yAxisLabel": y_axis_label,
                "yAxisProps": y_axis_props,
                **kwargs,
            },
        )

    def bar_chart(
        self,
        data: list,
        data_key: str,
        series: list[dict[str, Any]],
        *,
        bar_chart_props: Optional[dict[str, Any]] = None,
        bar_label_color: Optional[str] = None,
        bar_props: Optional[dict[str, Any]] = None,
        cursor_fill: Optional[str] = None,
        fill_opacity: Optional[float] = None,
        get_bar_color: Optional[Callable[[float, dict[str, Any]], str]] = None,
        grid_axis: Optional[Literal["none", "x", "y", "xy"]] = None,
        grid_color: Optional[str] = None,
        grid_props: Optional[dict[str, Any]] = None,
        key: Optional[str] = None,
        legend_props: Optional[dict[str, Any]] = None,
        max_bar_width: Optional[int] = None,
        min_bar_size: Optional[int] = None,
        orientation: Optional[Literal["horizontal", "vertical"]] = None,
        reference_lines: Optional[list[dict[str, Any]]] = None,
        right_y_axis_label: Optional[str] = None,
        right_y_axis_props: Optional[dict[str, Any]] = None,
        stroke_dasharray: Optional[Union[str, int]] = None,
        text_color: Optional[str] = None,
        tick_line: Optional[Literal["none", "x", "y", "xy"]] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        type: Optional[str] = None,  # noqa: A002
        unit: Optional[str] = None,
        value_label_props: Optional[dict[str, Any]] = None,
        with_bar_value_label: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_right_y_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_x_axis: Optional[bool] = None,
        with_y_axis: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_label: Optional[str] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Bar chart for categorical or time series data.

        Args:
            data (list): Dataset.
            data_key (str): X-axis data key.
            series (list[dict[str, Any]]): Series configuration.
            bar_chart_props (Optional[dict[str, Any]]): Chart container props.
            bar_label_color (Optional[str]): Value label color.
            bar_props (Optional[dict[str, Any]]): Bar props.
            cursor_fill (Optional[str]): Cursor overlay color.
            fill_opacity (Optional[float]): Bar fill opacity.
            get_bar_color (Optional[Callable[[float, dict[str, Any]], str]]): Dynamic color callback.
            grid_axis (Optional[Literal["none","x","y","xy"]]): Grid axis.
            grid_color (Optional[str]): Grid color.
            grid_props (Optional[dict[str, Any]]): Grid props.
            key (Optional[str]): Explicit element key.
            legend_props (Optional[dict[str, Any]]): Legend props.
            max_bar_width (Optional[int]): Max bar width.
            min_bar_size (Optional[int]): Min bar size.
            orientation (Optional[Literal["horizontal","vertical"]]): Orientation.
            reference_lines (Optional[list[dict[str, Any]]]): Reference lines.
            right_y_axis_label (Optional[str]): Secondary Y axis label.
            right_y_axis_props (Optional[dict[str, Any]]): Secondary Y axis props.
            stroke_dasharray (Optional[Union[str, int]]): Border dash pattern.
            text_color (Optional[str]): Text color.
            tick_line (Optional[Literal["none","x","y","xy"]]): Tick line display.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            type (Optional[str]): Chart type variant.
            unit (Optional[str]): Unit suffix.
            value_label_props (Optional[dict[str, Any]]): Value label props.
            with_bar_value_label (Optional[bool]): Show value labels above bars.
            with_legend (Optional[bool]): Show legend.
            with_right_y_axis (Optional[bool]): Enable right Y axis.
            with_tooltip (Optional[bool]): Show tooltip.
            with_x_axis (Optional[bool]): Show X axis.
            with_y_axis (Optional[bool]): Show Y axis.
            x_axis_label (Optional[str]): X axis label.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_label (Optional[str]): Y axis label.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the bar chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="barchart",
            key=key or self._new_text_id("barchart"),
            props={
                "data": data,
                "dataKey": data_key,
                "series": series,
                "barChartProps": bar_chart_props,
                "barLabelColor": bar_label_color,
                "barProps": bar_props,
                "cursorFill": cursor_fill,
                "fillOpacity": fill_opacity,
                "getBarColor": get_bar_color,
                "gridAxis": grid_axis,
                "gridColor": grid_color,
                "gridProps": grid_props,
                "legendProps": legend_props,
                "maxBarWidth": max_bar_width,
                "minBarSize": min_bar_size,
                "orientation": orientation,
                "referenceLines": reference_lines,
                "rightYAxisLabel": right_y_axis_label,
                "rightYAxisProps": right_y_axis_props,
                "strokeDasharray": stroke_dasharray,
                "textColor": text_color,
                "tickLine": tick_line,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "type": type,
                "unit": unit,
                "valueLabelProps": value_label_props,
                "withBarValueLabel": with_bar_value_label,
                "withLegend": with_legend,
                "withRightYAxis": with_right_y_axis,
                "withTooltip": with_tooltip,
                "withXAxis": with_x_axis,
                "withYAxis": with_y_axis,
                "xAxisLabel": x_axis_label,
                "xAxisProps": x_axis_props,
                "yAxisLabel": y_axis_label,
                "yAxisProps": y_axis_props,
                **kwargs,
            },
        )

    def line_chart(
        self,
        data: list,
        data_key: str,
        series: list[dict[str, Any]],
        *,
        key: Optional[str] = None,
        active_dot_props: Optional[dict[str, Any]] = None,
        connect_nulls: Optional[bool] = None,
        curve_type: Optional[str] = None,
        dot_props: Optional[dict[str, Any]] = None,
        fill_opacity: Optional[float] = None,
        gradient_stops: Optional[list[dict[str, Any]]] = None,
        grid_axis: Optional[str] = None,
        grid_color: Optional[str] = None,
        grid_props: Optional[dict[str, Any]] = None,
        legend_props: Optional[dict[str, Any]] = None,
        line_chart_props: Optional[dict[str, Any]] = None,
        line_props: Optional[dict[str, Any]] = None,
        orientation: Optional[str] = None,
        reference_lines: Optional[list[dict[str, Any]]] = None,
        right_y_axis_label: Optional[str] = None,
        right_y_axis_props: Optional[dict[str, Any]] = None,
        stroke_dasharray: Optional[str] = None,
        stroke_width: Optional[float] = None,
        text_color: Optional[str] = None,
        tick_line: Optional[str] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        type: Optional[str] = None,  # noqa: A002
        unit: Optional[str] = None,
        with_dots: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_point_labels: Optional[bool] = None,
        with_right_y_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_x_axis: Optional[bool] = None,
        with_y_axis: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_label: Optional[str] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Line chart for continuous data.

        Args:
            data (list): Dataset.
            data_key (str): X-axis data key.
            series (list[dict[str, Any]]): Series configuration.
            key (Optional[str]): Explicit element key.
            active_dot_props (Optional[dict[str, Any]]): Active dot props.
            connect_nulls (Optional[bool]): Connect across null values.
            curve_type (Optional[str]): Curve interpolation type.
            dot_props (Optional[dict[str, Any]]): Dot props.
            fill_opacity (Optional[float]): Area fill opacity for gradients.
            gradient_stops (Optional[list[dict[str, Any]]]): Gradient configuration.
            grid_axis (Optional[str]): Grid axis.
            grid_color (Optional[str]): Grid color.
            grid_props (Optional[dict[str, Any]]): Grid props.
            legend_props (Optional[dict[str, Any]]): Legend props.
            line_chart_props (Optional[dict[str, Any]]): Chart container props.
            line_props (Optional[dict[str, Any]]): Line props.
            orientation (Optional[str]): Chart orientation.
            reference_lines (Optional[list[dict[str, Any]]]): Reference lines.
            right_y_axis_label (Optional[str]): Secondary Y axis label.
            right_y_axis_props (Optional[dict[str, Any]]): Secondary Y axis props.
            stroke_dasharray (Optional[str]): Line dash pattern.
            stroke_width (Optional[float]): Line width.
            text_color (Optional[str]): Text color.
            tick_line (Optional[str]): Tick line display.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            type (Optional[str]): Chart type variant.
            unit (Optional[str]): Unit suffix.
            with_dots (Optional[bool]): Show dots.
            with_legend (Optional[bool]): Show legend.
            with_point_labels (Optional[bool]): Show point labels.
            with_right_y_axis (Optional[bool]): Enable right Y axis.
            with_tooltip (Optional[bool]): Show tooltip.
            with_x_axis (Optional[bool]): Show X axis.
            with_y_axis (Optional[bool]): Show Y axis.
            x_axis_label (Optional[str]): X axis label.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_label (Optional[str]): Y axis label.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the line chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="linechart",
            key=key or self._new_text_id("linechart"),
            props={
                "data": data,
                "dataKey": data_key,
                "series": series,
                "activeDotProps": active_dot_props,
                "connectNulls": connect_nulls,
                "curveType": curve_type,
                "dotProps": dot_props,
                "fillOpacity": fill_opacity,
                "gradientStops": gradient_stops,
                "gridAxis": grid_axis,
                "gridColor": grid_color,
                "gridProps": grid_props,
                "legendProps": legend_props,
                "lineChartProps": line_chart_props,
                "lineProps": line_props,
                "orientation": orientation,
                "referenceLines": reference_lines,
                "rightYAxisLabel": right_y_axis_label,
                "rightYAxisProps": right_y_axis_props,
                "strokeDasharray": stroke_dasharray,
                "strokeWidth": stroke_width,
                "textColor": text_color,
                "tickLine": tick_line,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "type": type,
                "unit": unit,
                "withDots": with_dots,
                "withLegend": with_legend,
                "withPointLabels": with_point_labels,
                "withRightYAxis": with_right_y_axis,
                "withTooltip": with_tooltip,
                "withXAxis": with_x_axis,
                "withYAxis": with_y_axis,
                "xAxisLabel": x_axis_label,
                "xAxisProps": x_axis_props,
                "yAxisLabel": y_axis_label,
                "yAxisProps": y_axis_props,
                **kwargs,
            },
        )

    def composite_chart(
        self,
        data: list,
        data_key: str,
        series: list[dict[str, Any]],
        *,
        key: Optional[str] = None,
        active_dot_props: Optional[dict[str, Any]] = None,
        area_props: Optional[dict[str, Any]] = None,
        bar_props: Optional[dict[str, Any]] = None,
        children: Optional[Any] = None,
        composed_chart_props: Optional[dict[str, Any]] = None,
        connect_nulls: Optional[bool] = None,
        curve_type: Optional[str] = None,
        dot_props: Optional[dict[str, Any]] = None,
        grid_axis: Optional[str] = None,
        grid_color: Optional[str] = None,
        grid_props: Optional[dict[str, Any]] = None,
        legend_props: Optional[dict[str, Any]] = None,
        line_props: Optional[dict[str, Any]] = None,
        max_bar_width: Optional[int] = None,
        min_bar_size: Optional[int] = None,
        reference_lines: Optional[list[dict[str, Any]]] = None,
        right_y_axis_label: Optional[str] = None,
        right_y_axis_props: Optional[dict[str, Any]] = None,
        stroke_dasharray: Optional[str] = None,
        stroke_width: Optional[int] = None,
        text_color: Optional[str] = None,
        tick_line: Optional[str] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        unit: Optional[str] = None,
        with_bar_value_label: Optional[bool] = None,
        with_dots: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_point_labels: Optional[bool] = None,
        with_right_y_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_x_axis: Optional[bool] = None,
        with_y_axis: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_label: Optional[str] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Composite chart that can combine bars, lines, and areas.

        Args:
            data (list): Dataset.
            data_key (str): X-axis data key.
            series (list[dict[str, Any]]): Series configuration.
            key (Optional[str]): Explicit element key.
            active_dot_props (Optional[dict[str, Any]]): Active dot props.
            area_props (Optional[dict[str, Any]]): Area props.
            bar_props (Optional[dict[str, Any]]): Bar props.
            children (Optional[Any]): Extra child elements.
            composed_chart_props (Optional[dict[str, Any]]): Chart container props.
            connect_nulls (Optional[bool]): Connect across null values.
            curve_type (Optional[str]): Curve interpolation type.
            dot_props (Optional[dict[str, Any]]): Dot props.
            grid_axis (Optional[str]): Grid axis.
            grid_color (Optional[str]): Grid color.
            grid_props (Optional[dict[str, Any]]): Grid props.
            legend_props (Optional[dict[str, Any]]): Legend props.
            line_props (Optional[dict[str, Any]]): Line props.
            max_bar_width (Optional[int]): Max bar width.
            min_bar_size (Optional[int]): Min bar size.
            reference_lines (Optional[list[dict[str, Any]]]): Reference lines.
            right_y_axis_label (Optional[str]): Secondary Y axis label.
            right_y_axis_props (Optional[dict[str, Any]]): Secondary Y axis props.
            stroke_dasharray (Optional[str]): Stroke dash pattern.
            stroke_width (Optional[int]): Line width.
            text_color (Optional[str]): Text color.
            tick_line (Optional[str]): Tick line display.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            unit (Optional[str]): Unit suffix.
            with_bar_value_label (Optional[bool]): Show value labels on bars.
            with_dots (Optional[bool]): Show dots on lines.
            with_legend (Optional[bool]): Show legend.
            with_point_labels (Optional[bool]): Show point labels on lines.
            with_right_y_axis (Optional[bool]): Enable right Y axis.
            with_tooltip (Optional[bool]): Show tooltip.
            with_x_axis (Optional[bool]): Show X axis.
            with_y_axis (Optional[bool]): Show Y axis.
            x_axis_label (Optional[str]): X axis label.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_label (Optional[str]): Y axis label.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the composite chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="compositechart",
            key=key or self._new_text_id("compositechart"),
            props={
                "data": data,
                "dataKey": data_key,
                "series": series,
                "activeDotProps": active_dot_props,
                "areaProps": area_props,
                "barProps": bar_props,
                "children": children,
                "composedChartProps": composed_chart_props,
                "connectNulls": connect_nulls,
                "curveType": curve_type,
                "dotProps": dot_props,
                "gridAxis": grid_axis,
                "gridColor": grid_color,
                "gridProps": grid_props,
                "legendProps": legend_props,
                "lineProps": line_props,
                "maxBarWidth": max_bar_width,
                "minBarSize": min_bar_size,
                "referenceLines": reference_lines,
                "rightYAxisLabel": right_y_axis_label,
                "rightYAxisProps": right_y_axis_props,
                "strokeDasharray": stroke_dasharray,
                "strokeWidth": stroke_width,
                "textColor": text_color,
                "tickLine": tick_line,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "unit": unit,
                "withBarValueLabel": with_bar_value_label,
                "withDots": with_dots,
                "withLegend": with_legend,
                "withPointLabels": with_point_labels,
                "withRightYAxis": with_right_y_axis,
                "withTooltip": with_tooltip,
                "withXAxis": with_x_axis,
                "withYAxis": with_y_axis,
                "xAxisLabel": x_axis_label,
                "xAxisProps": x_axis_props,
                "yAxisLabel": y_axis_label,
                "yAxisProps": y_axis_props,
                **kwargs,
            },
        )

    def donut_chart(
        self,
        data: list,
        *,
        chart_label: Optional[Union[str, int]] = None,
        end_angle: Optional[int] = None,
        key: Optional[str] = None,
        label_color: Optional[str] = None,
        labels_type: Optional[str] = None,
        padding_angle: Optional[int] = None,
        pie_chart_props: Optional[dict[str, Any]] = None,
        pie_props: Optional[dict[str, Any]] = None,
        size: Optional[int] = None,
        start_angle: Optional[int] = None,
        stroke_color: Optional[str] = None,
        stroke_width: Optional[int] = None,
        thickness: Optional[int] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_data_source: Optional[Literal["all", "segment"]] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        with_labels: Optional[bool] = None,
        with_labels_line: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Donut chart to visualize parts of a whole.

        Args:
            data (list): Dataset.
            chart_label (Optional[Union[str, int]]): Center label.
            end_angle (Optional[int]): End angle.
            key (Optional[str]): Explicit element key.
            label_color (Optional[str]): Label color.
            labels_type (Optional[str]): Label content type.
            padding_angle (Optional[int]): Angle between segments.
            pie_chart_props (Optional[dict[str, Any]]): Chart container props.
            pie_props (Optional[dict[str, Any]]): Pie props.
            size (Optional[int]): Chart size.
            start_angle (Optional[int]): Start angle.
            stroke_color (Optional[str]): Segment border color.
            stroke_width (Optional[int]): Segment border width.
            thickness (Optional[int]): Ring thickness.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_data_source (Optional[Literal["all","segment"]]): Tooltip data source.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            with_labels (Optional[bool]): Show labels.
            with_labels_line (Optional[bool]): Show label connector lines.
            with_tooltip (Optional[bool]): Show tooltip.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the donut chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="donutchart",
            key=key or self._new_text_id("donutchart"),
            props={
                "data": data,
                "chartLabel": chart_label,
                "endAngle": end_angle,
                "labelColor": label_color,
                "labelsType": labels_type,
                "paddingAngle": padding_angle,
                "pieChartProps": pie_chart_props,
                "pieProps": pie_props,
                "size": size,
                "startAngle": start_angle,
                "strokeColor": stroke_color,
                "strokeWidth": stroke_width,
                "thickness": thickness,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipDataSource": tooltip_data_source,
                "tooltipProps": tooltip_props,
                "withLabels": with_labels,
                "withLabelsLine": with_labels_line,
                "withTooltip": with_tooltip,
                **kwargs,
            },
        )

    def funnel_chart(
        self,
        data: list,
        *,
        funnel_chart_props: Optional[dict[str, Any]] = None,
        funnel_props: Optional[dict[str, Any]] = None,
        key: Optional[str] = None,
        label_color: Optional[str] = None,
        labels_position: Optional[Literal["left", "right", "inside"]] = None,
        size: Optional[int] = None,
        stroke_color: Optional[str] = None,
        stroke_width: Optional[int] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_data_source: Optional[Literal["all", "segment"]] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        value_formatter: Optional[Any] = None,
        with_labels: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Funnel chart for conversion or pipeline visualization.

        Args:
            data (list): Dataset.
            funnel_chart_props (Optional[dict[str, Any]]): Chart container props.
            funnel_props (Optional[dict[str, Any]]): Funnel props.
            key (Optional[str]): Explicit element key.
            label_color (Optional[str]): Label color.
            labels_position (Optional[Literal["left","right","inside"]]): Labels position.
            size (Optional[int]): Chart size.
            stroke_color (Optional[str]): Border color.
            stroke_width (Optional[int]): Border width.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_data_source (Optional[Literal["all","segment"]]): Tooltip data source.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            value_formatter (Optional[Any]): Value formatter.
            with_labels (Optional[bool]): Show labels.
            with_tooltip (Optional[bool]): Show tooltip.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the funnel chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="funnelchart",
            key=key or self._new_text_id("funnelchart"),
            props={
                "data": data,
                "funnelChartProps": funnel_chart_props,
                "funnelProps": funnel_props,
                "labelColor": label_color,
                "labelsPosition": labels_position,
                "size": size,
                "strokeColor": stroke_color,
                "strokeWidth": stroke_width,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipDataSource": tooltip_data_source,
                "tooltipProps": tooltip_props,
                "valueFormatter": value_formatter,
                "withLabels": with_labels,
                "withTooltip": with_tooltip,
                **kwargs,
            },
        )

    def pie_chart(
        self,
        data: list,
        *,
        end_angle: Optional[int] = None,
        key: Optional[str] = None,
        label_color: Optional[str] = None,
        labels_position: Optional[Literal["outside", "inside"]] = None,
        labels_type: Optional[Literal["value", "percent"]] = None,
        padding_angle: Optional[int] = None,
        pie_chart_props: Optional[dict[str, Any]] = None,
        pie_props: Optional[dict[str, Any]] = None,
        size: Optional[int] = None,
        start_angle: Optional[int] = None,
        stroke_color: Optional[str] = None,
        stroke_width: Optional[int] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_data_source: Optional[Literal["all", "segment"]] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        with_labels: Optional[bool] = None,
        with_labels_line: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Pie chart to visualize parts of a whole.

        Args:
            data (list): Dataset.
            end_angle (Optional[int]): End angle.
            key (Optional[str]): Explicit element key.
            label_color (Optional[str]): Label color.
            labels_position (Optional[Literal["outside","inside"]]): Labels position.
            labels_type (Optional[Literal["value","percent"]]): Label content.
            padding_angle (Optional[int]): Angle between segments.
            pie_chart_props (Optional[dict[str, Any]]): Chart container props.
            pie_props (Optional[dict[str, Any]]): Pie props.
            size (Optional[int]): Chart size.
            start_angle (Optional[int]): Start angle.
            stroke_color (Optional[str]): Border color.
            stroke_width (Optional[int]): Border width.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_data_source (Optional[Literal["all","segment"]]): Tooltip data source.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            with_labels (Optional[bool]): Show labels.
            with_labels_line (Optional[bool]): Show label connector lines.
            with_tooltip (Optional[bool]): Show tooltip.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the pie chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="piechart",
            key=key or self._new_text_id("piechart"),
            props={
                "data": data,
                "endAngle": end_angle,
                "labelColor": label_color,
                "labelsPosition": labels_position,
                "labelsType": labels_type,
                "paddingAngle": padding_angle,
                "pieChartProps": pie_chart_props,
                "pieProps": pie_props,
                "size": size,
                "startAngle": start_angle,
                "strokeColor": stroke_color,
                "strokeWidth": stroke_width,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipDataSource": tooltip_data_source,
                "tooltipProps": tooltip_props,
                "withLabels": with_labels,
                "withLabelsLine": with_labels_line,
                "withTooltip": with_tooltip,
                **kwargs,
            },
        )

    def radar_chart(
        self,
        data: list,
        data_key: str,
        series: list[dict[str, Any]],
        *,
        active_dot_props: Optional[dict[str, Any]] = None,
        dot_props: Optional[dict[str, Any]] = None,
        grid_color: Optional[str] = None,
        key: Optional[str] = None,
        legend_props: Optional[dict[str, Any]] = None,
        polar_angle_axis_props: Optional[dict[str, Any]] = None,
        polar_grid_props: Optional[dict[str, Any]] = None,
        polar_radius_axis_props: Optional[dict[str, Any]] = None,
        radar_chart_props: Optional[dict[str, Any]] = None,
        radar_props: Optional[dict[str, Any]] = None,
        text_color: Optional[str] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        with_dots: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_polar_angle_axis: Optional[bool] = None,
        with_polar_grid: Optional[bool] = None,
        with_polar_radius_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Radar chart for multi-dimensional categorical data.

        Args:
            data (list): Dataset.
            data_key (str): Key for category labels.
            series (list[dict[str, Any]]): Series configuration.
            active_dot_props (Optional[dict[str, Any]]): Active dot props.
            dot_props (Optional[dict[str, Any]]): Dot props.
            grid_color (Optional[str]): Grid color.
            key (Optional[str]): Explicit element key.
            legend_props (Optional[dict[str, Any]]): Legend props.
            polar_angle_axis_props (Optional[dict[str, Any]]): Polar angle axis props.
            polar_grid_props (Optional[dict[str, Any]]): Polar grid props.
            polar_radius_axis_props (Optional[dict[str, Any]]): Polar radius axis props.
            radar_chart_props (Optional[dict[str, Any]]): Chart container props.
            radar_props (Optional[dict[str, Any]]): Radar area/line props.
            text_color (Optional[str]): Text color.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            with_dots (Optional[bool]): Show dots.
            with_legend (Optional[bool]): Show legend.
            with_polar_angle_axis (Optional[bool]): Show angle axis.
            with_polar_grid (Optional[bool]): Show polar grid.
            with_polar_radius_axis (Optional[bool]): Show radius axis.
            with_tooltip (Optional[bool]): Show tooltip.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the radar chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="radarchart",
            key=key or self._new_text_id("radarchart"),
            props={
                "activeDotProps": active_dot_props,
                "data": data,
                "dataKey": data_key,
                "dotProps": dot_props,
                "gridColor": grid_color,
                "legendProps": legend_props,
                "polarAngleAxisProps": polar_angle_axis_props,
                "polarGridProps": polar_grid_props,
                "polarRadiusAxisProps": polar_radius_axis_props,
                "radarChartProps": radar_chart_props,
                "radarProps": radar_props,
                "series": series,
                "textColor": text_color,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "withDots": with_dots,
                "withLegend": with_legend,
                "withPolarAngleAxis": with_polar_angle_axis,
                "withPolarGrid": with_polar_grid,
                "withPolarRadiusAxis": with_polar_radius_axis,
                "withTooltip": with_tooltip,
                **kwargs,
            },
        )

    def scatter_chart(
        self,
        data: list,
        data_key: dict[str, str],
        *,
        grid_axis: Optional[str] = None,
        grid_color: Optional[str] = None,
        grid_props: Optional[dict[str, Any]] = None,
        labels: Optional[dict[str, str]] = None,
        legend_props: Optional[dict[str, Any]] = None,
        orientation: Optional[str] = None,
        point_labels: Optional[str] = None,
        reference_lines: Optional[list[dict[str, Any]]] = None,
        right_y_axis_label: Optional[str] = None,
        right_y_axis_props: Optional[dict[str, Any]] = None,
        scatter_chart_props: Optional[dict[str, Any]] = None,
        scatter_props: Optional[dict[str, Any]] = None,
        stroke_dasharray: Optional[Union[str, int]] = None,
        text_color: Optional[str] = None,
        tick_line: Optional[str] = None,
        tooltip_animation_duration: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        unit: Optional[dict[str, str]] = None,
        value_formatter: Optional[Any] = None,
        with_legend: Optional[bool] = None,
        with_right_y_axis: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_x_axis: Optional[bool] = None,
        with_y_axis: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_label: Optional[str] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Scatter chart for visualizing correlation between two variables.

        Args:
            data (list): Dataset.
            data_key (dict[str, str]): Mapping for x/y keys.
            grid_axis (Optional[str]): Grid axis.
            grid_color (Optional[str]): Grid color.
            grid_props (Optional[dict[str, Any]]): Grid props.
            labels (Optional[dict[str, str]]): Axis labels.
            legend_props (Optional[dict[str, Any]]): Legend props.
            orientation (Optional[str]): Orientation.
            point_labels (Optional[str]): Point labels key.
            reference_lines (Optional[list[dict[str, Any]]]): Reference lines.
            right_y_axis_label (Optional[str]): Secondary Y axis label.
            right_y_axis_props (Optional[dict[str, Any]]): Secondary Y axis props.
            scatter_chart_props (Optional[dict[str, Any]]): Chart container props.
            scatter_props (Optional[dict[str, Any]]): Scatter props.
            stroke_dasharray (Optional[Union[str, int]]): Stroke dash pattern.
            text_color (Optional[str]): Text color.
            tick_line (Optional[str]): Tick line display.
            tooltip_animation_duration (Optional[int]): Tooltip animation duration.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            unit (Optional[dict[str, str]]): Axis units.
            value_formatter (Optional[Any]): Value formatter.
            with_legend (Optional[bool]): Show legend.
            with_right_y_axis (Optional[bool]): Enable right Y axis.
            with_tooltip (Optional[bool]): Show tooltip.
            with_x_axis (Optional[bool]): Show X axis.
            with_y_axis (Optional[bool]): Show Y axis.
            x_axis_label (Optional[str]): X axis label.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_label (Optional[str]): Y axis label.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            key (Optional[str]): Explicit element key.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the scatter chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="scatterchart",
            key=key or self._new_text_id("scatterchart"),
            props={
                "data": data,
                "dataKey": data_key,
                "gridAxis": grid_axis,
                "gridColor": grid_color,
                "gridProps": grid_props,
                "labels": labels,
                "legendProps": legend_props,
                "orientation": orientation,
                "pointLabels": point_labels,
                "referenceLines": reference_lines,
                "rightYAxisLabel": right_y_axis_label,
                "rightYAxisProps": right_y_axis_props,
                "scatterChartProps": scatter_chart_props,
                "scatterProps": scatter_props,
                "strokeDasharray": stroke_dasharray,
                "textColor": text_color,
                "tickLine": tick_line,
                "tooltipAnimationDuration": tooltip_animation_duration,
                "tooltipProps": tooltip_props,
                "unit": unit,
                "valueFormatter": value_formatter,
                "withLegend": with_legend,
                "withRightYAxis": with_right_y_axis,
                "withTooltip": with_tooltip,
                "withXAxis": with_x_axis,
                "withYAxis": with_y_axis,
                "xAxisLabel": x_axis_label,
                "xAxisProps": x_axis_props,
                "yAxisLabel": y_axis_label,
                "yAxisProps": y_axis_props,
                **kwargs,
            },
        )

    def bubble_chart(
        self,
        data: list[dict[str, Any]],
        data_key: dict[str, str],
        range: tuple[int, int],  # noqa: A002
        *,
        color: Optional[str] = None,
        grid_color: Optional[str] = None,
        key: Optional[str] = None,
        label: Optional[str] = None,
        scatter_props: Optional[dict[str, Any]] = None,
        text_color: Optional[str] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        with_tooltip: Optional[bool] = None,
        x_axis_props: Optional[dict[str, Any]] = None,
        y_axis_props: Optional[dict[str, Any]] = None,
        z_axis_props: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Bubble chart for three-dimensional data (x, y, z-size).

        Args:
            data (list[dict[str, Any]]): Dataset with x, y, z.
            data_key (dict[str, str]): Mapping for x/y/z keys.
            range (tuple[int, int]): Bubble size range.
            color (Optional[str]): Bubble color.
            grid_color (Optional[str]): Grid color.
            key (Optional[str]): Explicit element key.
            label (Optional[str]): Series label.
            scatter_props (Optional[dict[str, Any]]): Scatter props.
            text_color (Optional[str]): Text color.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            with_tooltip (Optional[bool]): Show tooltip.
            x_axis_props (Optional[dict[str, Any]]): X axis props.
            y_axis_props (Optional[dict[str, Any]]): Y axis props.
            z_axis_props (Optional[dict[str, Any]]): Z axis props.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the bubble chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="bubblechart",
            key=key or self._new_text_id("bubblechart"),
            props={
                "data": data,
                "dataKey": data_key,
                "range": range,
                "color": color,
                "gridColor": grid_color,
                "label": label,
                "scatterProps": scatter_props,
                "textColor": text_color,
                "tooltipProps": tooltip_props,
                "withTooltip": with_tooltip,
                "xAxisProps": x_axis_props,
                "yAxisProps": y_axis_props,
                "zAxisProps": z_axis_props,
                **kwargs,
            },
        )

    def radial_bar_chart(
        self,
        data: list[dict[str, Any]],
        data_key: str,
        *,
        bar_size: Optional[int] = None,
        empty_background_color: Optional[str] = None,
        end_angle: Optional[int] = None,
        key: Optional[str] = None,
        legend_props: Optional[dict[str, Any]] = None,
        radial_bar_chart_props: Optional[dict[str, Any]] = None,
        radial_bar_props: Optional[dict[str, Any]] = None,
        start_angle: Optional[int] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        with_background: Optional[bool] = None,
        with_labels: Optional[bool] = None,
        with_legend: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Radial bar chart for circular bar visualizations.

        Args:
            data (list[dict[str, Any]]): Dataset.
            data_key (str): Value key.
            bar_size (Optional[int]): Bar thickness.
            empty_background_color (Optional[str]): Empty background color.
            end_angle (Optional[int]): End angle.
            key (Optional[str]): Explicit element key.
            legend_props (Optional[dict[str, Any]]): Legend props.
            radial_bar_chart_props (Optional[dict[str, Any]]): Chart container props.
            radial_bar_props (Optional[dict[str, Any]]): Bar props.
            start_angle (Optional[int]): Start angle.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            with_background (Optional[bool]): Show circular background.
            with_labels (Optional[bool]): Show labels.
            with_legend (Optional[bool]): Show legend.
            with_tooltip (Optional[bool]): Show tooltip.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the radial bar chart element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="radialbarchart",
            key=key or self._new_text_id("radialbarchart"),
            props={
                "data": data,
                "dataKey": data_key,
                "barSize": bar_size,
                "emptyBackgroundColor": empty_background_color,
                "endAngle": end_angle,
                "legendProps": legend_props,
                "radialBarChartProps": radial_bar_chart_props,
                "radialBarProps": radial_bar_props,
                "startAngle": start_angle,
                "tooltipProps": tooltip_props,
                "withBackground": with_background,
                "withLabels": with_labels,
                "withLegend": with_legend,
                "withTooltip": with_tooltip,
                **kwargs,
            },
        )

    def sparkline_chart(
        self,
        data: list[Union[int, float, None]],
        *,
        area_props: Optional[dict[str, Any]] = None,
        color: Optional[str] = None,
        connect_nulls: Optional[bool] = None,
        curve_type: Optional[str] = None,
        fill_opacity: Optional[float] = None,
        key: Optional[str] = None,
        stroke_width: Optional[int] = None,
        trend_colors: Optional[dict[str, Any]] = None,
        with_gradient: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Compact sparkline chart for trends.

        Args:
            data (list[Union[int, float, None]]): Dataset.
            area_props (Optional[dict[str, Any]]): Area props.
            color (Optional[str]): Line/area color.
            connect_nulls (Optional[bool]): Connect across null values.
            curve_type (Optional[str]): Curve interpolation type.
            fill_opacity (Optional[float]): Area fill opacity.
            key (Optional[str]): Explicit element key.
            stroke_width (Optional[int]): Line width.
            trend_colors (Optional[dict[str, Any]]): Trend color overrides.
            with_gradient (Optional[bool]): Fill with gradient.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the sparkline element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="sparkline",
            key=key or self._new_text_id("sparkline"),
            props={
                "data": data,
                "areaProps": area_props,
                "color": color,
                "connectNulls": connect_nulls,
                "curveType": curve_type,
                "fillOpacity": fill_opacity,
                "strokeWidth": stroke_width,
                "trendColors": trend_colors,
                "withGradient": with_gradient,
                **kwargs,
            },
        )

    def heatmap(
        self,
        data: dict[str, Union[int, float]],
        *,
        colors: Optional[list[str]] = None,
        domain: Optional[tuple[Union[int, float], Union[int, float]]] = None,
        end_date: Optional[Union[str, Any]] = None,
        first_day_of_week: Optional[int] = None,
        font_size: Optional[int] = None,
        gap: Optional[int] = None,
        get_rect_props: Optional[Any] = None,
        get_tooltip_label: Optional[Any] = None,
        key: Optional[str] = None,
        month_labels: Optional[list[str]] = None,
        months_labels_height: Optional[int] = None,
        rect_radius: Optional[int] = None,
        rect_size: Optional[int] = None,
        start_date: Optional[Union[str, Any]] = None,
        tooltip_props: Optional[dict[str, Any]] = None,
        weekday_labels: Optional[list[str]] = None,
        weekdays_labels_width: Optional[int] = None,
        with_month_labels: Optional[bool] = None,
        with_outside_dates: Optional[bool] = None,
        with_tooltip: Optional[bool] = None,
        with_weekday_labels: Optional[bool] = None,
        **kwargs: Any,
    ) -> "RLBuilder":
        """
        Calendar heatmap for visualizing value intensity over dates.

        Args:
            data (dict[str, Union[int, float]]): Mapping of ISO date -> value.
            colors (Optional[list[str]]): Color scale.
            domain (Optional[tuple[Union[int, float], Union[int, float]]]): Min/max domain.
            end_date (Optional[Union[str, Any]]): End date.
            first_day_of_week (Optional[int]): First day of the week.
            font_size (Optional[int]): Font size for labels.
            gap (Optional[int]): Gap between cells.
            get_rect_props (Optional[Any]): Custom rect props callback.
            get_tooltip_label (Optional[Any]): Tooltip label callback.
            key (Optional[str]): Explicit element key.
            month_labels (Optional[list[str]]): Month labels.
            months_labels_height (Optional[int]): Month labels height.
            rect_radius (Optional[int]): Cell border radius.
            rect_size (Optional[int]): Cell size.
            start_date (Optional[Union[str, Any]]): Start date.
            tooltip_props (Optional[dict[str, Any]]): Tooltip props.
            weekday_labels (Optional[list[str]]): Weekday labels.
            weekdays_labels_width (Optional[int]): Weekday labels width.
            with_month_labels (Optional[bool]): Show month labels.
            with_outside_dates (Optional[bool]): Show dates outside range.
            with_tooltip (Optional[bool]): Show tooltip.
            with_weekday_labels (Optional[bool]): Show weekday labels.
            kwargs: Additional props to set.

        Returns:
            RLBuilder: A nested builder scoped to the heatmap element.
        """
        return self._create_builder_element(  # type: ignore[return-value]
            name="heatmap",
            key=key or self._new_text_id("heatmap"),
            props={
                "data": data,
                "colors": colors,
                "domain": domain,
                "endDate": end_date,
                "firstDayOfWeek": first_day_of_week,
                "fontSize": font_size,
                "gap": gap,
                "getRectProps": get_rect_props,
                "getTooltipLabel": get_tooltip_label,
                "monthLabels": month_labels,
                "monthsLabelsHeight": months_labels_height,
                "rectRadius": rect_radius,
                "rectSize": rect_size,
                "startDate": start_date,
                "tooltipProps": tooltip_props,
                "weekdayLabels": weekday_labels,
                "weekdaysLabelsWidth": weekdays_labels_width,
                "withMonthLabels": with_month_labels,
                "withOutsideDates": with_outside_dates,
                "withTooltip": with_tooltip,
                "withWeekdayLabels": with_weekday_labels,
                **kwargs,
            },
        )
