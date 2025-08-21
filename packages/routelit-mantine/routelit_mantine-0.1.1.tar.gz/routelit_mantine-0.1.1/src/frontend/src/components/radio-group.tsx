import { Radio } from "@mantine/core";
import GenericGroup from "./generic-group";

type RadioGroupProps = React.ComponentProps<typeof Radio.Group> & {
  groupProps?: React.ComponentProps<typeof import("@mantine/core").Flex>;
  options?: Array<{
    label: string;
    value: string;
  }>;
};

function RadioGroup({
  children,
  options,
  groupProps,
  ...props
}: RadioGroupProps) {
  const renderGroup = (children: React.ReactNode, groupProps: Record<string, unknown>) => (
    <Radio.Group {...groupProps}>{children}</Radio.Group>
  );

  const renderItem = (item: { label: string; value: string }) => {
    const { value, label, ...itemProps } = item;
    return (
      <Radio {...itemProps} key={value} value={value} label={label} />
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

export default RadioGroup;
