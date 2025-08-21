import { Checkbox, Flex } from "@mantine/core";
import GenericGroup from "./generic-group";

type CheckboxGroupProps = React.ComponentProps<typeof Checkbox.Group> & {
  groupProps?: React.ComponentProps<typeof Flex>;
  options?: Array<{
    label: string;
    value: string;
  }>;
};

function CheckboxGroup({
  children,
  options,
  groupProps,
  ...props
}: CheckboxGroupProps) {
  const renderGroup = (children: React.ReactNode, groupProps: Record<string, unknown>) => (
    <Checkbox.Group {...groupProps}>{children}</Checkbox.Group>
  );

  const renderItem = (item: { label: string; value: string }) => {
    const { value, label, ...itemProps } = item;
    return (
      <Checkbox {...itemProps} key={value} value={value} label={label} />
    );
  };

  return (
    <GenericGroup
      options={options}
      groupProps={groupProps}
      renderGroup={renderGroup}
      renderItem={renderItem}
      {...props}
    >
      {children}
    </GenericGroup>
  );
}

export default CheckboxGroup;
