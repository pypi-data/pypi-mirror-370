import { Switch, Flex } from "@mantine/core";
import GenericGroup from "./generic-group";

type SwitchGroupProps = React.ComponentProps<typeof Switch.Group> & {
  groupProps?: React.ComponentProps<typeof Flex>;
  options?: Array<{
    label: string;
    value: string;
  }>;
};

function SwitchGroup({
  children,
  options,
  groupProps,
  ...props
}: SwitchGroupProps) {
  const renderGroup = (children: React.ReactNode, groupProps: Record<string, unknown>) => (
    <Switch.Group {...groupProps}>{children}</Switch.Group>
  );

  const renderItem = (item: { label: string; value: string }) => {
    const { value, label, ...itemProps } = item;
    return (
      <Switch {...itemProps} key={value} value={value} label={label} />
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

export default SwitchGroup;
