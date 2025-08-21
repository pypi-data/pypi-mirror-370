import { Chip } from "@mantine/core";
import GenericGroup from "./generic-group";

type ChipGroupProps = React.ComponentProps<typeof Chip.Group> & {
  groupProps?: React.ComponentProps<typeof import("@mantine/core").Flex>;
  options?: Array<{
    label: string;
    value: string;
  }>;
};

function ChipGroup({
  children,
  options,
  groupProps,
  ...props
}: ChipGroupProps) {
  const renderGroup = (children: React.ReactNode, groupProps: Record<string, unknown>) => (
    <Chip.Group {...groupProps}>{children}</Chip.Group>
  );

  const renderItem = (item: { label: string; value: string }) => {
    const { value, label, ...itemProps } = item;
    return (
      <Chip {...itemProps} key={value} value={value}>
        {label}
      </Chip>
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

export default ChipGroup;
